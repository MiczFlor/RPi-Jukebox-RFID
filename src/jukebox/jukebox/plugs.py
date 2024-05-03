# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder
"""
A plugin package with some special functionality

Plugins packages are python packages that are dynamically loaded. From these packages only a subset of objects is exposed
through the plugs.call interface. The python packages can use decorators or dynamic function call to register (callable)
objects.

The python package name may be different from the name the package is registered under in plugs. This allows to load different
python packages for a specific feature based on a configuration file. Note: Python package are still loaded as regular
python packages and can be accessed by normal means

If you want to provide additional functionality to the same feature (probably even for run-time switching)
you can implement a Factory Pattern using this package. Take a look at volume.py as an example.

**Example:** Decorate a function for auto-registering under it's own name:

    import jukebox.plugs as plugs
    @plugs.register
    def func1(param):
        pass

**Example:** Decorate a function for auto-registering under a new name:

    @plugs.register(name='better_name')
    def func2(param):
        pass

**Example:** Register a function during run-time under it's own name:

    def func3(param):
        pass
    plugs.register(func3)

**Example:** Register a function during run-time under a new name:

    def func4(param):
        pass
    plugs.register(func4, name='other_name', package='other_package')

**Example:** Decorate a class for auto registering during initialization,
including all methods (see _register_class for more info):

    @plugs.register(auto_tag=True)
    class MyClass1:
        pass

**Example:** Register a class instance, from which only report is a callable method through the plugs interface:

    class MyClass2:
        @plugs.tag
        def report(self):
            pass
    myinst2 = MyClass2()
    plugin.register(myinst2, name='myinst2')

Naming convention:

* package
  * Either a python package
  * or a plugin package (which is the python package but probably loaded under a different name inside plugs)
* plugin
  * An object from the package that can be accessed through the plugs call function (i.e. a function or a class instance)
  * The string name to above object
* name
  * The string name of the plugin object for registration
* method
  * In case the object is a class instance a bound method to call from the class instance
  * The string name to above object

"""

import importlib
import inspect
import functools
import sys
import logging
import threading
from typing import (
    overload,
    cast,
    Callable,
    Type,
    Dict,
    List,
    Mapping,
    Iterable,
    Optional,
    Union,
    Any)
import traceback

logger = logging.getLogger('jb.plugin')
logger_call = logging.getLogger('jb.plugin.call')

# Do I want to use this?
PluginType = Callable[..., Any]

# Modules must be loaded with plugs.load(...) instead import()
# In some cases, it is necessary to load a module normally used as
# plugin with an regular import (e.g. automodule in Sphinx docs)
# Loading plugs first, and setting this variable to True, allows to do so
# In this case, initializer functions are not executed!
ALLOW_DIRECT_IMPORTS: bool = False

# ---------------------------------------------------------------------------
# Global thread-related stuff
# ---------------------------------------------------------------------------
# Module level-lock for serializing execution calls via call(...)
# Non-reentrant should be sufficient, but let's stay on the safe side for now
_lock_module = threading.RLock()


def _acquire_lock():
    """
    Acquire the module-level lock for serializing access to shared data.

    This should be released with _releaseLock().
    """
    if _lock_module:
        _lock_module.acquire()


def _release_lock():
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    if _lock_module:
        _lock_module.release()


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
class PluginPackageClass:
    """
    A local data class for holding all information about a loaded plugin package
    """
    def __init__(self, loaded_from: str):
        # The package reference is dynamically typed as we do not know what it contains
        # https://docs.python.org/3/library/typing.html#the-any-type
        # The reference to the loaded python module
        self._module: Any = None
        # The registered plugin callables
        self._plugins: Dict[str, Callable] = {}
        # The name of the python module this package was loaded from
        # (The loaded_as information is available from _PLUGINS.keys())
        self._loaded_from: str = loaded_from
        # List of functions called directly after the individual module is loaded
        self._initializer: List[Callable] = []
        # List of functions called after ALL modules have been loaded
        self._finalizer: List[Callable] = []
        # List of functions called at exit of main program
        self._atexit: List[Callable] = []

    @property
    def loaded_from(self):
        return self._loaded_from

    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, value):
        if self._module is not None:
            raise AttributeError("Cannot override already set module!")
        self._module = value

    @property
    def plugins(self):
        return self._plugins

    @plugins.setter
    def plugins(self, value):
        self._plugins = value

    @property
    def initializer(self):
        return self._initializer

    @initializer.setter
    def initializer(self, value):
        self._initializer = value

    @property
    def finalizer(self):
        return self._finalizer

    @finalizer.setter
    def finalizer(self, value):
        self._finalizer = value

    @property
    def atexit(self):
        return self._atexit

    @atexit.setter
    def atexit(self, value):
        self._atexit = value


# Maintain a list of all loaded paackges with their loaded plugin callables and further information
# Maps loaded_as -> plugins, where PluginPackageClass contains all information about the loaded plugins from that package
_PLUGINS: Dict[str, PluginPackageClass] = {}
# Maintain a list of modules that have been loaded though the plugs module
# (with their python module name and the loaded_as package name)
# Maps loaded_from -> loaded_as
_PACKAGE_MAP: Dict[str, str] = {}
# Container for all packages with attempted load but failed to load error free
# Could be during import (package will no be available) or during initialize (package available but not initialized)
_PLUGINS_FAILED: Dict[str, PluginPackageClass] = {}


def _deduce_package_origin(obj: Any) -> Union[str, None]:
    """
    Given an object try to find which python package it belongs to in plugs.py terms

    :return: None if failed for up level error handling / Exception raising
    """
    return getattr(obj, '__module__', None)


def _enlist(package, plugin_obj, plugin_name, *, replace=False):
    """Internal function for putting the plugin_obj in the storage container"""
    if package not in _PLUGINS:
        raise NameError(f"Package '{package}' not registered")
    if (replace is False) and (plugin_name in _PLUGINS[package].plugins):
        raise NameError(f"Plugin with '{package}.{plugin_name}' already registered "
                        f"(points to: '{_PLUGINS[package].loaded_from}.{_PLUGINS[package].plugins[plugin_name].__name__}')")
    _PLUGINS[package].plugins[plugin_name] = plugin_obj
    return plugin_obj


def _register_obj(plugin: Any,
                  name: Optional[str] = None,
                  package: Optional[str] = None, *,
                  replace: bool = False) -> Any:
    """
    Register a non-class plugin object for a package. Use via the generic 'register' function.

    This function can register:
    - function in decorator style (cannot use name and package)
    - function as dynamic function style
    - bound method as dynamic function style
    - class instance as dynamic function style. Methods of class instances are only made callable,
    if they are tagged with the decorator @plugin.tag!

    :param plugin: Function to register
    :param name: Register with this name, if None the name is that of the function. Only of not used as decorator
    :param package: Register plugin with the package, if None use the configured plugin package for the python package
    :return: The object itself
    """
    # Note: During loading of python package, the attribute plugs_loaded_as is not yet available
    # After load we could also use: sys.modules[plugin.__module__].plugs_loaded_as
    plugin_origin = _deduce_package_origin(plugin)
    if plugin_origin is None:
        # This is a bit sneaky: All the object we allow to be called stem from some module
        # Let's see if that works out ...
        raise TypeError(f"Trying to register object with incompatible type: '{type(plugin)}")
    if package is None:
        if plugin_origin in _PACKAGE_MAP.keys():
            package = _PACKAGE_MAP[plugin_origin]
        elif ALLOW_DIRECT_IMPORTS:
            package = plugin_origin
            _PACKAGE_MAP[plugin_origin] = plugin_origin
            _PLUGINS[plugin_origin] = PluginPackageClass(plugin_origin)
            setattr(sys.modules[plugin_origin], 'plugs_loaded_as', package)
        else:
            raise KeyError(f"Module '{plugin_origin}' not loaded as plugin! "
                           f"Did you wrongly use import {plugin_origin}?")

    if inspect.isfunction(plugin):
        if plugin.__qualname__ != plugin.__name__:
            raise TypeError(f"Registering of unbound methods not allowed! Offending method: '{plugin.__qualname__}'")
        name = name or plugin.__name__
        logger.debug(f"Enlisting function '{plugin_origin}.{plugin.__name__}' as '{package}.{name}' ({type(plugin)})")
    elif inspect.ismethod(plugin):
        name = name or plugin.__qualname__
        logger.debug(f"Enlisting bound method '{plugin_origin}.{plugin.__qualname__}' as '{package}.{name}' "
                     f"({type(plugin)})")
    elif not inspect.isclass(plugin) and not inspect.ismodule(plugin) \
            and not inspect.istraceback(plugin) and not inspect.iscode(plugin) and not inspect.isframe(plugin) \
            and hasattr(plugin, '__class__'):
        # Class instance (and probably a few other things we are not filtering at the moment)
        if (name is None) or len(name) == 0:
            raise NameError("Argument 'name' is mandatory if registering a class instance")
        name = name
        logger.debug(f"Enlisting an instance of class '{plugin_origin}.{plugin.__class__.__name__}' as '{package}.{name}'")
    else:
        raise TypeError(f"Trying to register object with incompatible type: '{type(plugin)}")
    return _enlist(package, plugin, name, replace=replace)


def _register_class(cls: Type, auto_tag: bool = False) -> Type:
    """
    Decorator for classes. Decorated classes will auto-register when initialized

    The decorated class will have two additional parameters in the constructor! See __init__ below.

    Methods are not automatically made callable via the plugs interface! Only those methods tagged
    with the decorator @plugin.tag can be called via the plugs interface.

    Developers note:
    It is not guaranteed that the instantiation takes place during the loading of the module.
    For this case we store the name of the plugin package which we get
    during loading of the module into a Class variable. This is later used when the instance is registered.

    :param cls: The class to decorate
    :param auto_tag: Automatically tag all methods as callable through the plugs interface
    :return: The decorated class
    """
    package_origin = _deduce_package_origin(cls)
    if package_origin is None:
        raise TypeError("Could not deduce package origin. Maybe you are trying to register the wrong type?")

    logger.debug(f"Decorating class {cls.__module__}.{cls.__name__} for auto-assignment "
                 f"into package '{_PACKAGE_MAP[package_origin]}'")

    @functools.wraps(cls, updated=())
    # https://www.javaer101.com/en/article/38088804.html
    class IClass(cls):  # type: ignore
        plugs_decorated = 1
        plugs_package = _PACKAGE_MAP[cast(str, package_origin)]

        def __init__(self, *args, plugin_name, plugin_register=True, **kwargs):
            """
            Decorated class initializer for auto-registering every instance with plugins

            :param args: Arguments passed to the base class
            :param kwargs: Arguments passed to the base class
            :param plugin_name: the name under which the instance shall be registered
            :param plugin_register: if false, prevents the instance from auto-registering itself
            """
            super().__init__(*args, **kwargs)
            logger.debug(f"Instantiating decorated class '{cls.__module__}.{IClass.__name__}' "
                         f"and register as '{IClass.plugs_package}.{plugin_name}'")
            if plugin_register:
                _register_obj(plugin=self, name=plugin_name, package=IClass.plugs_package)

    # Auto-tag all functions and methods (except __init__)
    if auto_tag:
        logger.debug(f"Auto-tagging all methods and functions of class '{cls.__module__}.{IClass.__name__}'")
        for m in [*inspect.getmembers(IClass, predicate=inspect.ismethod),
                  *inspect.getmembers(IClass, predicate=inspect.isfunction)]:
            if m[0] != '__init__':
                setattr(m[1], 'plugs_callable', True)

    return IClass


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------

@overload
def register(plugin: Callable) -> Callable:
    """1-level decorator around a function"""
    pass


@overload
def register(plugin: Type) -> Any:
    """Signature: 1-level decorator around a class"""
    pass


@overload
def register(*, name: str, package: Optional[str] = None) -> Callable:
    """Signature: 2-level decorator around a function"""
    pass


@overload
def register(*, auto_tag: bool = False, package: Optional[str] = None) -> Type:
    """Signature: 2-level decorator around a class"""
    pass


@overload
def register(plugin: Callable[..., Any] = None, *,
             name: Optional[str] = None,
             package: Optional[str] = None,
             replace: bool = False) -> Callable:
    """Signature: Run-time registration of function / class instance / bound method"""
    pass


def register(plugin: Optional[Callable] = None, *,
             name: Optional[str] = None,
             package: Optional[str] = None,
             replace: bool = False,
             auto_tag: bool = False) -> Callable:
    """
    A generic decorator / run-time function to register plugin module callables

    The functions comes in five distinct signatures for 5 use cases:

    1. ``@plugs.register``: decorator for a class w/o any arguments
    2. ``@plugs.register``: decorator for a function w/o any arguments
    3. ``@plugs.register(auto_tag=bool)``: decorator for a class with 1 arguments
    4. ``@plugs.register(name=name, package=package)``: decorator for a function with 1 or 2 arguments
    5. ``plugs.register(plugin, name=name, package=package)``: run-time registration of
        * function
        * bound method
        * class instance

    For more documentation see the functions
    * :func:`_register_obj`
    * :func:`_register_class`

    See the examples in Module :mod:`plugs` how to use this decorator / function

    :param plugin:
    :param name:
    :param package:
    :param replace:
    :param auto_tag:
    :return:
    """

    # print(f"{plugin}")
    with _lock_module:
        if plugin is None:
            # If the plugin is None, we assume this is used as decorator with params
            # Case A: Used as 2-level decorator around a function
            # Attention: very strong 2-level decorator voodoo. The actual function must be extracted by an inner decorator
            # Argument plugin is never used, others depend on class / function
            def inner_function(obj):
                if inspect.isclass(obj):
                    return _register_class(obj, auto_tag=auto_tag)
                else:
                    return _register_obj(obj, name=name, package=package, replace=replace)
            return inner_function
        if inspect.isclass(plugin):
            # Case B: 1-level decorator around a class
            return _register_class(cast(Type, plugin), auto_tag=False)
        else:
            # Everything else: throw it at object registration
            # Case C.1: Used as 1-level decorator on a function
            # Case D.1: Used as 1-level decorator on an unbound method inside a class: This is an error caught by register_obj
            # Case E.1: Used as function to register a function
            # Case E.2: Used as function to register an entire class instance
            # Case E.3: Used as function to register a bound method
            return _register_obj(plugin, name=name, package=package, replace=replace)


def tag(func: Callable) -> Callable:
    """
    Method decorator for tagging a method as callable through the plugs interface

    Note that the instantiated class must still be registered as plugin object
    (either with the class decorator or dynamically)

    :param func: function to decorate
    :return: the function
    """
    logger.debug(f"Tagging {func.__qualname__}")
    if not (inspect.isfunction(func) and func.__qualname__ != func.__name__):
        raise AttributeError("plugs.tag is a decorator only for unbound class methods")
    setattr(func, 'plugs_callable', True)
    return func


def initialize(func: Callable) -> Callable:
    """
    Decorator for functions that shall be called by the plugs package directly after the module is loaded

    :param func: Function to decorate
    :return: The function itself
    """
    with _lock_module:
        plugin_origin = _deduce_package_origin(func)
        if plugin_origin is None:
            raise TypeError(f"Could not deduce corresponding package of {func}")
        if not ALLOW_DIRECT_IMPORTS:
            _PLUGINS[_PACKAGE_MAP[plugin_origin]].initializer.append(func)
        return func


def finalize(func: Callable) -> Callable:
    """
    Decorator for functions that shall be called by the plugs package directly after ALL modules are loaded

    :param func: Function to decorate
    :return: The function itself
    """
    with _lock_module:
        plugin_origin = _deduce_package_origin(func)
        if plugin_origin is None:
            raise TypeError(f"Could not deduce corresponding package of {func}")
        if not ALLOW_DIRECT_IMPORTS:
            _PLUGINS[_PACKAGE_MAP[plugin_origin]].finalizer.append(func)
        return func


def atexit(func: Callable[[int], Any]) -> Callable[[int], Any]:
    """
    Decorator for functions that shall be called by the plugs package directly after at exit of program.

    > [!IMPORTANT]
    > There is no automatism as in atexit.atexit. The function plugs.shutdown() must be explicitly called
    > during the shutdown procedure of your program. This is by design, so you can choose the exact situation in your
    > shutdown handler.

    The atexit-functions are called with a single integer argument, which is passed down from plugin.exit(int)
    It is intended for passing down the signal number that initiated the program termination

    :param func: Function to decorate
    :return: The function itself
    """
    with _lock_module:
        plugin_origin = _deduce_package_origin(func)
        if plugin_origin is None:
            raise TypeError(f"Could not deduce corresponding package of {func}")
        if not ALLOW_DIRECT_IMPORTS:
            _PLUGINS[_PACKAGE_MAP[plugin_origin]].atexit.append(func)
        return func


def load(package: str, load_as: Optional[str] = None, prefix: Optional[str] = None):
    """
    Loads a python package as plugin package

    Executes a regular python package load. That means a potentially existing `__init__.py` is executed.
    Decorator `@register` can by used to register functions / classes / class istances as plugin callable
    Decorator `@initializer` can be used to tag functions that shall be called after package loading
    Decorator `@finalizer` can be used to tag functions that shall be called after ALL plugin packges have been loaded
    Instead of using `@initializer`, you may of course use `__init__.py`

    Python packages may be loaded under a different plugs package name. Python packages must be unique and the name under
    which they are loaded as plugin package also.

    :param package: Python package to load as plugin package
    :param load_as: Plugin package registration name. If None the name is the python's package simple name
    :param prefix: Prefix to python package to create fully qualified name. This is used only to locate the python package
        and ignored otherwise. Useful if all the plugin module are in a dedicated folder
    :return:
    """
    load_as = load_as or package
    if prefix is not None:
        package = f"{prefix}.{package}"

    logger.info(f"Loading plugin '{package}' as '{load_as}'")
    if package in _PACKAGE_MAP:
        msg = f"Package '{package}' already loaded as '{_PACKAGE_MAP[package]}'. Cannot be loaded twice!"
        logger.error(msg)
        raise NameError(msg)
    if load_as in _PLUGINS:
        msg = f"Plugin module already registered: '{load_as}' (from '{_PLUGINS[load_as].loaded_from}')."
        logger.error(msg)
        raise NameError(msg)

    _PACKAGE_MAP[package] = load_as
    _PLUGINS[load_as] = PluginPackageClass(package)
    try:
        _PLUGINS[load_as].module = importlib.import_module(f'{package}', 'pkg')
        setattr(_PLUGINS[load_as].module, 'plugs_loaded_as', load_as)
    except Exception as e:
        # Clear the failed plugin registration
        _PLUGINS.__delitem__(load_as)
        _PACKAGE_MAP.__delitem__(package)
        # Store attempted but failed loads for later reference
        _PLUGINS_FAILED[load_as] = PluginPackageClass(package)
        logger.error(f"Failed to load package: {package}")
        raise e

    for func in _PLUGINS[load_as].initializer:
        logger.debug(f"Package load initializer: calling {load_as}.{func.__name__}()")
        try:
            func()
        except Exception as e:
            _PLUGINS_FAILED[load_as] = PluginPackageClass(package)
            raise e


def load_all_named(packages_named: Mapping[str, str], prefix: Optional[str] = None, ignore_errors=False):
    """Load all packages in packages_named with mapped names

    :param packages_named: Dict[load_as, package]
    """
    for load_as, package in packages_named.items():
        try:
            load(package, load_as, prefix)
        except Exception as e:
            if ignore_errors:
                logger.error(f"Ignoring failed package load for '{package}'")
                logger.error(f"Reason: {e.__class__.__name__}: {e}")
                logger.error(f"Detailed reason:\n{traceback.format_exc()}")
            else:
                raise e


def load_all_unnamed(packages_unnamed: Iterable[str], prefix: Optional[str] = None, ignore_errors=False):
    """Load all packages in packages_unnamed with default names"""
    for package in packages_unnamed:
        try:
            load(package, prefix=prefix)
        except Exception as e:
            if ignore_errors:
                logger.error(f"Ignoring failed package load for '{package}'")
                logger.error(f"Reason: {e.__class__.__name__}: {e}")
                logger.error(f"Detailed reason:\n{traceback.format_exc()}")
            else:
                raise e


def load_all_finalize(ignore_errors=False):
    """Calls all functions registered with @finalize from all loaded modules in the order they were loaded

    This must be executed after the last plugin package is loaded"""
    # Preserve loading-order for finalize order:
    # Order of modules in dictionary is preserved in Python >= 3.7.
    #  ... Else use OrdredDict for _PACKAGES??
    # https://realpython.com/python-ordereddict/
    assert sys.version_info.major >= 3 and sys.version_info.minor >= 7
    for loaded_as, pack in _PLUGINS.items():
        for func in pack.finalizer:
            logger.debug(f"Package load finalizer: calling {loaded_as}.{func.__name__}()")
            try:
                func()
            except Exception as e:
                if ignore_errors:
                    logger.error(f"Ignoring failed package load finalizer: '{loaded_as}.{func.__name__}()'")
                    logger.error(f"Reason: {e.__class__.__name__}: {e.__str__()}")
                    logger.error(f"Detailed reason:\n{traceback.format_exc()}")
                else:
                    raise e


def close_down(**kwargs) -> Any:
    """
    Calls all functions registered with @atexit from all loaded modules in reverse order of module load order

    Modules are processed in reverse order. Several at-exit tagged functions of a single module are processed
    in the order of registration.

    Errors raised in functions are suppressed to ensure all plugins are processed
    :return:
    """
    results = []
    assert sys.version_info.major >= 3 and sys.version_info.minor >= 7
    for loaded_as, pack in reversed(list(_PLUGINS.items())):
        for func in pack.atexit:
            logger.debug(f"Package closing atexit: calling {loaded_as}.{func.__name__}({kwargs})")
            try:
                results.append(func(**kwargs))
            except Exception as e:
                logger.error(f"Ignoring failed package atexit function: '{loaded_as}.{func.__name__}()'")
                logger.error(f"Reason: {e.__class__.__name__}: {e.__str__()}")
                logger.error(f"Detailed reason:\n{traceback.format_exc()}")
    return results


def dereference(package: str, plugin: str, method: Optional[str] = None, *,
                args=None, kwargs=None):
    func = get(package, plugin, method)
    if args is None:
        args = ()
    else:
        # Make the argument passing more fail-safe:
        # args should an argument list, but these cases are converted:
        # - if a single argument is passed, wrap is in a list first
        # - if a string is passed, it is iterable but a single argument
        if isinstance(args, str):
            args = [args]
        else:
            try:
                args.__iter__()
            except AttributeError:
                args = [args]
    if kwargs is None:
        kwargs = {}
    if (not callable(func)) or inspect.isclass(func):
        msg = f"{package}.{plugin}"
        if method is not None:
            msg += f".{method}"
        raise TypeError(f"Not callable: '{msg}'")
    if method is not None:
        if not getattr(func, 'plugs_callable', False):
            raise TypeError(f"Attribute '{package}.{plugin}.{method}' not tagged as plugin callable")
    return func, args, kwargs


def _call(package: str, plugin: str, method: Optional[str] = None, *,
          args=None, kwargs=None, as_thread: bool = False, thread_name: Optional[str] = None) -> Any:
    """
    The internals of the call functionality. See :func:`call` for documentation!

    This low-level core is not thread safe! Surrounding function must lock the module properly.
    """
    if logger_call.isEnabledFor(logging.DEBUG):
        m = f".{method}" if method is not None else ''
        logger_call.debug(f"Calling: {package}.{plugin}{m}(args={args}, kwargs={kwargs})")

    func, args, kwargs = dereference(package, plugin, method, args=args, kwargs=kwargs)
    if as_thread is True:
        l_thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True, name=thread_name)
        l_thread.start()
        return l_thread
    else:
        return func(*args, **kwargs)


def call(package: str, plugin: str, method: Optional[str] = None, *,
         args=(), kwargs=None, as_thread: bool = False, thread_name: Optional[str] = None) -> Any:
    """
    Call a function/method from the loaded plugins

    If a plugin is a function or a callable instance of a class, this is equivalent to

    ``package.plugin(*args, **kwargs)``

    If plugin is a class instance from which a method is called, this is equivalent to the followig.
    Also remember, that method must have the attribute ``plugin_callable = True``

    ``package.plugin.method(*args, **kwargs)``

    Calls are serialized by a thread lock. The thread lock is shared with call_ignore_errors.

    > [!NOTE]
    > There is no logger in this function as they all belong up-level where the exceptions are handled.
    > If you want logger messages instead of exceptions, use :func:`call_ignore_errors`

    :param package: Name of the plugin package in which to look for function/class instance
    :param plugin: Function name or instance name of a class
    :param method: Method name when accessing a class instance' method. Leave at *None* if unneeded.
    :param as_thread: Run the callable in separate daemon thread.
        There is no return value from the callable in this case! The return value is the thread object.
        Also note that Exceptions in the Thread must be handled in the Thread and are not propagated to the main Thread.
        All threads are started as daemon threads with terminate upon main program termination.
        There is not stop-thread mechanism. This is intended for short lived threads.
    :param thread_name: Name of the thread
    :param args: Arguments passed to callable
    :param kwargs: Keyword arguments passed to callable
    :return: The return value from the called function, or, if started as thread the thread object
    """
    with _lock_module:
        result = _call(package, plugin, method, args=args, kwargs=kwargs, as_thread=as_thread, thread_name=thread_name)
    return result


def call_ignore_errors(package: str, plugin: str, method: Optional[str] = None, *,
                       args=(), kwargs=None, as_thread: bool = False, thread_name: Optional[str] = None) -> Any:
    """
    Call a function/method from the loaded plugins ignoring all raised Exceptions.

    Errors get logged.

    See :func:`call` for parameter documentation.
    """
    _acquire_lock()
    try:
        result = _call(package, plugin, method, args=args, kwargs=kwargs, as_thread=as_thread, thread_name=thread_name)
    except Exception as e:
        result = None
        name = f'{package}.{plugin}'
        if method is not None:
            name += f'.{method}'
        logger.error(f"Ignoring failed call: '{name}(args={args}, kwargs={kwargs})'")
        logger.error(f"Reason: {e.__class__.__name__}: {e}")
        logger.error(f"Detailed reason:\n{traceback.format_exc()}")
    finally:
        _release_lock()
    return result


def exists(package: str, plugin: Optional[str] = None, method: Optional[str] = None) -> bool:
    """Check if an object is registered within the plugs package"""
    with _lock_module:
        if package not in _PLUGINS:
            return False
        if plugin is None:
            return True
        if plugin not in _PLUGINS[package].plugins:
            return False
        if method is None:
            return True
        return hasattr(_PLUGINS[package].plugins[plugin], method)


def get(package: str, plugin: Optional[str] = None, method: Optional[str] = None) -> Any:
    """Get a plugs-package registered object

    The return object depends on the number of parameters

    * 1 argument: Get the python module reference for the plugs *package*
    * 2 arguments: Get the plugin reference for the plugs *package.plugin*
    * 3 arguments: Get the plugin reference for the plugs *package.plugin.method*

    """
    with _lock_module:
        pack = _PLUGINS.get(package, None)
        if pack is None:
            raise NameError(f"Package '{package}' not registered")
        if plugin is None:
            if method is not None:
                raise TypeError("Argument 'method' specified, but not argument 'plugin'")
            return _PLUGINS[package].module
        plug = _PLUGINS[package].plugins.get(plugin, None)
        if plug is None:
            raise NameError(f"Plugin object '{plugin}' not registered in package '{package}'")
        if method is None:
            return plug
        func = getattr(plug, method, None)
        if func is None:
            raise NameError(f"Plugin object '{package}.{plugin}' has not attribute '{method}'")
        return func


def loaded_as(module_name: str) -> str:
    """Return the plugin name a python module is loaded as"""
    with _lock_module:
        if module_name not in _PACKAGE_MAP.keys():
            raise KeyError(f"Not a loaded module: {module_name}")
        return _PACKAGE_MAP[module_name]


def delete(package: str, plugin: Optional[str] = None, ignore_errors=False):
    """Delete a plugin object from the registered plugs callables

    > [!NOTE]
    > This does not 'unload' the python module. It merely makes it un-callable via plugs!
    """
    with _lock_module:
        if exists(package, plugin):
            if plugin is None:
                _PACKAGE_MAP.__delitem__(_PLUGINS[package].loaded_from)
                _PLUGINS.__delitem__(package)
            else:
                _PLUGINS[package].plugins.__delitem__(plugin)
        elif not ignore_errors:
            p = "" if plugin is None else f".{plugin}"
            raise NameError(f"Not registered: '{package}{p}'. Cannot delete it!")


def dump_plugins(stream):
    """Write a human readable summary of all plugin callables to stream"""
    with _lock_module:
        width = 127
        print('*' * width, file=stream)
        print("Loaded plugins:", file=stream)
        print('*' * width, file=stream)
        for package, plugins in _PLUGINS.items():
            description = (plugins.module.__doc__ or "").split('\n\n', 1)[0].strip('\n ')
            print(f"Package: '{package}' loaded from: '{plugins.loaded_from}'", file=stream)
            print(f"    {description}\n", file=stream)
            for name, obj in _PLUGINS[package].plugins.items():
                description = (obj.__doc__ or "").split('\n\n', 1)[0].strip('\n ')
                t = f"{name} [instance]"
                if callable(obj):
                    t = f"{name}{inspect.signature(obj)}"
                print(f"    {t:29}: {description}", file=stream)
                if not callable(obj):
                    for fname, fobj in [*inspect.getmembers(obj, predicate=inspect.ismethod),
                                        *inspect.getmembers(obj, predicate=inspect.isfunction)]:
                        if hasattr(fobj, 'plugs_callable'):
                            description = (fobj.__doc__ or "").split('\n\n', 1)[0].strip('\n ')
                            sign = f"{fname}{inspect.signature(fobj)}"
                            print(f"        {sign:25}: {description}", file=stream)
                    print("", file=stream)
            print("", file=stream)
        print('*' * width, file=stream)


def summarize():
    """Create a reference summary of all plugin callables in dictionary format"""
    with _lock_module:
        all_callables = {}
        for package, plugins in _PLUGINS.items():
            for name, obj in _PLUGINS[package].plugins.items():
                description = (obj.__doc__ or "").split('\n\n', 1)[0].strip('\n ')
                if callable(obj):
                    sign = f"{inspect.signature(obj)}"
                    fullname = f"{package}.{name}"
                    entry = {'package': package,
                             'plugin': name,
                             'signature': sign,
                             'description': description}
                    all_callables[fullname] = entry
                else:
                    for fname, fobj in [*inspect.getmembers(obj, predicate=inspect.ismethod),
                                        *inspect.getmembers(obj, predicate=inspect.isfunction)]:
                        if hasattr(fobj, 'plugs_callable'):
                            description = (fobj.__doc__ or "").split('\n\n', 1)[0].strip('\n ')
                            sign = f"{fname}{inspect.signature(fobj)}"
                            fullname = f"{package}.{name}.{fname}"
                            entry = {'package': package,
                                     'plugin': name,
                                     'method': fname,
                                     'signature': sign,
                                     'description': description}
                            all_callables[fullname] = entry
        return all_callables


def _indent(doc, spaces=4):
    lines = doc.split('\n')
    for i in range(0, len(lines)):
        lines[i] = " " * spaces + lines[i]
    return "\n".join(lines)


def generate_help_rst(stream):
    """Write a reference of all plugin callables in Restructured Text format"""
    with _lock_module:
        print("RPC Command Reference", file=stream)
        print("***********************\n\n", file=stream)
        print("This file provides a summary of all the callable functions through the RPC. It depends on the "
              "loaded modules\n", file=stream)
        print(".. contents::\n", file=stream)
        for package, plugins in _PLUGINS.items():

            print(f"Module: {package}", file=stream)
            print("-------------------------------------------\n\n", file=stream)

            # description = (get(package).__doc__ or "").strip('\n ')
            # description = re.sub(r'\n', '\n    ', description, flags=re.MULTILINE)
            # print(f"    {description}\n\n", file=stream)

            print(f"**loaded_from**:    {plugins.loaded_from}\n", file=stream)

            # From package only get header line
            description = (get(package).__doc__ or "").split('\n\n', 1)[0].strip('\n ')
            print(f"{inspect.cleandoc(description)}\n\n", file=stream)

            for name, obj in _PLUGINS[package].plugins.items():
                # description = inspect.cleandoc(obj.__doc__ or "")
                description = _indent(inspect.cleandoc(obj.__doc__ or ""), 4)
                if callable(obj):
                    fullname = f"{package}.{name}"
                    sign = f"{inspect.signature(obj)}"
                    print(f".. py:function:: {fullname}{sign}", file=stream)
                    print("    :noindex:\n", file=stream)
                    print(f"{description}\n\n", file=stream)
                else:
                    for fname, fobj in [*inspect.getmembers(obj, predicate=inspect.ismethod),
                                        *inspect.getmembers(obj, predicate=inspect.isfunction)]:
                        if hasattr(fobj, 'plugs_callable'):
                            description = _indent(inspect.cleandoc(fobj.__doc__ or ""), 4)
                            sign = f"{inspect.signature(fobj)}"
                            fullname = f"{package}.{name}.{fname}"
                            print(f".. py:function:: {fullname}{sign}", file=stream)
                            print("    :noindex:\n", file=stream)
                            print(f"{description}\n\n", file=stream)
        print("\n\nGeneration notes", file=stream)
        print("-------------------------------------------\n\n", file=stream)
        print("This is an automatically generated file from the loaded plugins:\n", file=stream)
        for la, lf in get_all_loaded_packages().items():
            print(f"* *{la}*: {lf}", file=stream)
        fp = get_all_failed_packages()
        if len(fp) > 0:
            print("\n.. error::\n", file=stream)
            print("   These packages failed to load or loaded with errors:\n", file=stream)
            for la, lf in fp.items():
                print(f"   * *{la}*: {lf}", file=stream)
            print("\n   This reference may be incomplete!\n", file=stream)


def get_all_loaded_packages() -> Dict[str, str]:
    """Report a short summary of all loaded packages

    :return: Dictionary of the form `{loaded_as: loaded_from, ...}`"""
    with _lock_module:
        return {k: _PLUGINS[k].loaded_from for k in _PLUGINS.keys()}


def get_all_failed_packages() -> Dict[str, str]:
    """Report those packages that did not load error free

    > [!NOTE]
    > Package could fail to load
    > * altogether: these package are not registered
    > * partially: during initializer, finalizer functions: The package is loaded,
    > but the function did not execute error-free
    >
    > Partially loaded packages are listed in both _PLUGINS and _PLUGINS_FAILED

    :return: Dictionary of the form `{loaded_as: loaded_from, ...}`"""
    with _lock_module:
        return {k: _PLUGINS_FAILED[k].loaded_from for k in _PLUGINS_FAILED.keys()}
