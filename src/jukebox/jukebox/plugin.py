import importlib
import inspect
import functools
import logging
import threading

logger = logging.getLogger('jb.plugin')

# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


# Collects all loaded modules
# Format {module1_name: module1, module2_name: module2}
modules = {}

# Collects all registered callables
# format {module1_name: {func1_name: func1, func2_name: func2, ...}, module2_name: {...}}
callables = {'default': {}}

# Stores the name of the module currently being loaded
current_module = 'default'


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _enlist(obj, name, plugin_name):
    """
    Enlist the object into global callables register
    :param obj: Object to enlist
    :param name: Enlist with this name
    :return: The object again
    """
    if name in callables[plugin_name]:
        msg = f"There is an object with the same name '{name}' already registered in module '{plugin_name}'"
        logger.error(msg)
        raise NameError(msg)
    if plugin_name == 'default':
        logger.warning(f"Plugin name is 'default'! While enlisting {name}.")
    callables[plugin_name][name] = obj
    return obj


def _register_obj(obj, name_as=None, module_name=None):
    """
    Register a non-class object for the (current) plugin module. It is recommended to use the generic 'register' function.

    Register
    - function in decorator style (cannot use name_as and module_name)
    - function as dynamic function style
    - bound method as dynamic function style
    - class instance as dynamic function style

    :param obj: Function to register
    :param name_as: Register with this name, if None the name is that of the function. Only of not used as decorator
    :param module_name: Register with the plugin_module, if None use current_module
    :return: The object itself
    """
    module_name = module_name or current_module
    if inspect.isfunction(obj):
        if obj.__qualname__ != obj.__name__:
            raise TypeError(f"Registering of unbound methods not allowed! Offending method: '{obj.__qualname__}'")
        name = name_as or obj.__name__
        logger.debug(f"Enlisting function '{obj.__name__}' as '{name}' in module '{module_name}' "
                     f"in plugin {module_name} with type {type(obj)}")
    elif inspect.ismethod(obj):
        name = name_as or obj.__qualname__
        logger.debug(f"Enlisting bound method '{obj.__qualname__}' as '{name}' in module '{module_name}' "
                     f"in plugin {module_name} with type {type(obj)}")
    elif not inspect.isclass(obj) and not inspect.ismodule(obj) \
            and not inspect.istraceback(obj) and not inspect.iscode(obj) and not inspect.isframe(obj) \
            and hasattr(obj, '__class__'):
        # Class instance (and probably a few other things we are not filtering at the moment)
        if name_as is None or len(name_as) == 0:
            raise TypeError("Argument 'name' is mandatory if registering a class instance")
        name = name_as
        logger.debug(f"Enlisting an instance of class '{obj.__class__}' as {name} in plugin {module_name} "
                     f"with type {type(obj)}")
    else:
        raise TypeError(f"Trying to register object with incompatible type: '{type(obj)}")
    return _enlist(obj, name, module_name)


def _register_class(cls):
    """
    Decorator for classes: Classes will auto-register when initialized

    The decorated class will have two additional parameters in the constructor: see below!

    Developers note:
    It is not guaranteed that the instantiation takes place during the loading of the module.
    (Not very easy to achieve, but possible). For this case we store the name of the plugin_module which we get
    during loading of the module into a Class variable. This is later used when the instance is registered.

    :param cls: The class to decorate
    :return: The decorated class
    """
    @functools.wraps(cls, updated=())
    class IClass(cls):
        decorated = 1
        plugin_module = current_module

        def __init__(self, *args, plugin_name, plugin_register=True, **kwargs):
            """
            Decorated class initializer for auto-registering every instance with plugins

            :param args: Arguments passed to the base class
            :param kwargs: Arguments passed to the base class
            :param plugin_name: the name under which the instance shall be registered
            :param plugin_register: if false, prevents the instance from auto-registering itself
            """
            super().__init__(*args, **kwargs)
            logger.debug(f"Instantiating decorated class '{IClass.__name__}' "
                         f"in module {IClass.plugin_module} as '{plugin_name}'")
            if plugin_register:
                _register_obj(self, plugin_name, IClass.plugin_module)

    return IClass


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


def load(name, load_as=None):
    """
    Load the plugin name

    Loads the python submodule with the name as plugin.
    That means a potentially existing __init__.py is executed.
    On top, if a function init() exists at module's top-level it is executed.
    Use decorators or __init__.py (with or w/o init()) to register all RPC callables of submodule with plugin module

    If there already is a module loaded with the same name, an error is raised

    :param name: python module name
    :param load_as: Register with this plugin name, if None the name is the submodule name
    :return:
    """
    global current_module
    current_module = load_as or name
    logger.debug(f"Loading plugin '{name}' as '{current_module}'")
    if current_module in callables:
        msg = f"There is a plugin module with the same name already registered: '{current_module}'. Ignoring the new module..."
        current_module = 'default'
        logger.error(msg)
        raise NameError(msg)

    callables[current_module] = {}
    try:
        modules[current_module] = importlib.import_module(f'components.{name}', 'pkg')
        if hasattr(modules[current_module], 'init'):
            modules[current_module].init()
    except Exception as e:
        logger.error(f"Failed to load volume module_name: {name}")
        logger.error(f"Reason: {e}")
        raise e
    finally:
        current_module = 'default'


def call(module_name, obj_name, method_name=None, *, args=(), kwargs=None, as_thread=False):
    """
    Call a function/method from the loaded plugins

    - module_name.obj_name(*args, **kwargs)
        where obj_name is a function or a callable instance of a class
    - module_name.obj_name.method_name(*args, **kwargs)
        where obj_name is a class instance
    - module_name.obj_name().method_name(*args, **kwargs)
        where obj_name is a callable instance of a class, and method_name is invoked on whatever it returns
        (this allows for factory patterns: obj_name is a factory getter with default value)
        How to differentiate: if obj_name is callable? -> Careful with classes that contain __call__ but also provide other
        methods that need to be accessible through the RPC
        --> Does not work out, the factory needs to be accessible for set/get_default and list ...
    - module_name.obj_name(*args2, **kwargs2).method_name(*args, **kwargs)
        Not callable at the moment ...

    Developers notes:
        There is no logger in this function as they all belong uplevel where the exceptions are handled
        If you want logger messages instead of exceptions, use call_ignore_errors

    :param module_name: Name of the module in which to look for function/class instance
    :param obj_name: Function name or instance name of a class
    :param method_name: Method name when accessing a class instance' method. Leave at None if unneeded.
    :param as_thread: Run the callable in separate daemon thread.
    There is no return value from the callable in this case! Also note that Exceptions in the Thread must be handled
    in the Thread and are not propagated to the main Thread. All threads are started as daemon threads with terminate
    upon main program termination. There is not stop-thread mechanism. This is intended for short lived threads.
    :param args: Arguments passed to callable
    :param kwargs: Keyword arguments passed to callable
    :return: The return value from the called function (if not started as thread)
    """
    if kwargs is None:
        kwargs = {}
    if module_name not in callables:
        # AttributeError or NameError ?
        raise NameError(f"Unknown plugin with name: '{module_name}'")
    plugin_callables = callables[module_name]
    if obj_name not in plugin_callables:
        # AttributeError or NameError ?
        raise NameError(f"Requested object not registered as plugin callable: '{obj_name}' in module '{module_name}'")
    # In RPC context we want to be able to call:
    # - functions
    # - class instances that have a __call__ function
    # - arbitrary methods from class instances
    # but not
    # - classes themselves (i.e. the initializer) as the reference to the instance in not stored
    #   (and these can only be registered by circumventing the use of the register functions!)
    func = plugin_callables[obj_name]
    if method_name is None:
        if (not callable(func)) or inspect.isclass(func):
            raise TypeError(f"Requested object not callable: '{obj_name}' in module '{module_name}'")
    else:
        func = getattr(func, method_name, None)
        if func is None:
            raise AttributeError(f"Object '{obj_name}' in module '{module_name}' has no attribute '{method_name}'")
        if not callable(func):
            raise TypeError(f"Attribute '{method_name}' not callable of object '{obj_name}' in module '{module_name}'")

    if as_thread is True:
        l_thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        l_thread.start()
        return
    else:
        return func(*args, **kwargs)


def call_ignore_errors(module_name, obj_name, method_name=None, *, args=(), kwargs=None, as_thread=False):
    """
    Call a function/method from the loaded plugins suppressing all errors

    Identical to function 'call', but suppress all errors. Only produce logger messages.

    Note: When call is dispatched as a separate thread, errors in this thread are NOT caught! In this case the
    thread terminates with an Exception and a stack trace. No logger entry is generated!
    """
    result = None
    try:
        result = call(module_name, obj_name, method_name, args=args, kwargs=kwargs, as_thread=as_thread)
    except Exception as e:
        func = f'{module_name}.{obj_name}'
        if method_name is not None:
            func += f'.{method_name}'
        logger.error(f"Call failed: '{func}(args={args}, kwargs={kwargs})'")
        logger.error(f"Reason: {e}")
    return result


def exists(module_name, obj_name=None, method_name=None):
    """
    Check if the plugin element is registered

    :return: Boolean
    """
    if module_name not in callables:
        return False
    if obj_name is not None:
        if obj_name not in callables[module_name]:
            return False
        if method_name is not None:
            obj = callables[module_name][obj_name]
            return hasattr(obj, method_name)
    elif method_name is not None:
        return False
    return True


def register(arg1, arg2=None, arg3=None):
    """
    A generic decorator / run-time function to register plugin module callables

    The generic nature of this function means that the meaning of the arguments changes significantly depending on the
    use case. The function comes in three signatures:

    (A) @plugin.register: decorator for class or function w/o any arguments
    (B) @plugin.register(name_as, module_name=None): decorator for function with 1 or 2 arguments
    (C) plugin.register(obj, name_as=None, module_name=None): registration function for
        - function
        - bound method
        - class instance

    For argument documentation and background see
        _register_obj
        _register_class

    See the examples below how to use this decorator / function

    It is recommended to use this decorator / function for all the registration needs instead of
    _register_obj and _register_class! But see these functions for additional documentation

    Example: Decorate a function for auto-registering under it's own name
    >>> import plugin
    >>> @plugin.register
    >>> def func1(param):
    >>>     pass

    Example: Decorate a function for auto-registering under a new name
    >>> @plugin.register('better_name')
    >>> def func2(param):
    >>>     pass

    Example: Register a function during run-time under it's own name
    >>> def func3(param):
    >>>     pass
    >>> plugin.register(func3)

    Example: Register a function during run-time under a new name
    >>> def func4(param):
    >>>     pass
    >>> plugin.register(func4, 'other_name')

    Example: Decorate a class for auto registering during initialization (see register_class for more info)
    >>> @plugin.register
    >>> class MyClass1:
    >>>     pass

    Example: Register a class instance
    >>> class MyClass2:
    >>>     pass
    >>> myinst2 = MyClass2()
    >>> plugin.register(myinst2, 'myinst2')

    By default everything is registerd under the curent module. This only works if the subpackge is loaded with plugin.load()
    and all dynamic registration is done during the loading of the subpackage. In case the is a need to register
    a function or instance outside the subpackage initialization, you must specify the module under which it shall be
    registered explicitly. Decorated classes store the module reference internally

    Example: Register a function during run-time under it's own name and specify the module name explicitly
    >>> def func5(param):
    >>>     pass
    >>> plugin.register(func5, func5.__name__, 'mymodule')
    or equally (but less readable):
    >>> plugin.register(func5, arg3='mymodule')

    Example: As above but for a class instance
    >>> class MyClass3:
    >>>     pass
    >>> myinst3 = MyClass3()
    >>> plugin.register(myinst3, 'myinst3', 'mymodule')

    Example: Register a function with a decorator under a different module name explicitly. Note that 'other_module'
    must already exist as a registered module. (This is only for completeness sake. I cannot see any use case.)
    >>> @plugin.register(func6.__name__, 'other_module')
    >>> def func6(param):
    >>>     pass
    """
    logger.debug(f"Register: arg1 with '{arg1}' of type 'type{arg1}'; arg2 with '{arg2}' of type 'type{arg2}'; "
                 f"arg3 with '{arg3}' of type 'type{arg3}'")
    if type(arg1) == str:
        # Attention: very strong Decorator Voodoo:
        # Case A: Used as 2-level decorator around a function
        # If the first argument is a string, we assume this is used as decorator with params (hopefully around a function)
        # 2-level decorator means
        #   arg1: name under which the func shall be registered
        #   arg2: for cross-module registering: function shall be registered under this module name rather than current_module
        #   The actual function must be extracted by an inner decorator
        # Misuse: if used as decorator with params, but on a class or a method --> special error message for easier debug
        def inner_function(func):
            # This error would also be caught in register_obj, but with a very misleading error message
            # as the root cause is very different.
            if not inspect.isfunction(func):
                raise TypeError(f"Decorator takes no arguments on object : '{func.__name__}' of type '{type(func)}")
            return _register_obj(func, arg1, arg2)
        return inner_function
    elif inspect.isclass(arg1):
        # Case B: Decorator around a class
        return _register_class(arg1)
    else:
        # Throw it at dynamic object registration
        # Case C.1: Used as 1-level decorator on a function: arg1 function, arg2, arg3 are default (None)
        # Case D.1: Used as 1-level decorator on an unbound method inside a class: This is an error caught by register_obj
        # Case E.1: Used as function to register a function
        # Case E.2: Used as function to register an entire class instance
        # Case E.3: Used as function to register a bound method
        #         : arg1 is obj, arg2 may be new register_as name, arg3 may be module_name
        return _register_obj(arg1, arg2, arg3)
