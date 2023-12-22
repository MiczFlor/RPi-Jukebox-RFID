<!-- markdownlint-disable -->

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `jukebox.plugs`
A plugin package with some special functionality 

Plugins packages are python packages that are dynamically loaded. From these packages only a subset of objects is exposed through the plugs.call interface. The python packages can use decorators or dynamic function call to register (callable) objects. 

The python package name may be different from the name the package is registered under in plugs. This allows to load different python packages for a specific feature based on a configuration file. Note: Python package are still loaded as regular python packages and can be accessed by normal means 

If you want to provide additional functionality to the same feature (probably even for run-time switching) you can implement a Factory Pattern using this package. Take a look at volume.py as an example. 

**Example:** Decorate a function for auto-registering under it's own name:
``` 

     import jukebox.plugs as plugs      @plugs.register      def func1(param):          pass 

**Example:** Decorate a function for auto-registering under a new name:
``` 

     @plugs.register(name='better_name')      def func2(param):          pass 

**Example:** Register a function during run-time under it's own name:
``` 

     def func3(param):          pass      plugs.register(func3) 

**Example:** Register a function during run-time under a new name:
``` 

     def func4(param):          pass      plugs.register(func4, name='other_name', package='other_package') 

```
**Example:** Decorate a class for auto registering during initialization, including all methods (see _register_class for more info):
``` 

     @plugs.register(auto_tag=True)      class MyClass1:          pass 

**Example:** Register a class instance, from which only report is a callable method through the plugs interface:
``` 

     class MyClass2:          @plugs.tag          def report(self):              pass      myinst2 = MyClass2()      plugin.register(myinst2, name='myinst2') 

```
Naming convention: 

package  1. Either a python package  2. or a plugin package (which is the python package but probably loaded under a different name inside plugs) 

plugin  1. An object from the package that can be accessed through the plugs call function (i.e. a function or a class instance)  2. The string name to above object 

name  The string name of the plugin object for registration 

method  1. In case the object is a class instance a bound method to call from the class instance  2. The string name to above object 

**Global Variables**
---------------
- **ALLOW_DIRECT_IMPORTS**

---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L393"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `register`

```python
register(
    plugin: Optional[Callable] = None,
    name: Optional[str] = None,
    package: Optional[str] = None,
    replace: bool = False,
    auto_tag: bool = False
) → Callable
```

A generic decorator / run-time function to register plugin module callables 

The functions comes in five distinct signatures for 5 use cases: 

1. ``@plugs.register``: decorator for a class w/o any arguments 2. ``@plugs.register``: decorator for a function w/o any arguments 3. ``@plugs.register(auto_tag=bool)``: decorator for a class with 1 arguments 4. ``@plugs.register(name=name, package=package)``: decorator for a function with 1 or 2 arguments 5. ``plugs.register(plugin, name=name, package=package)``: run-time registration of 

 * function  * bound method  * class instance 

For more documentation see the functions 

 * :func:`_register_obj`  * :func:`_register_class` 

See the examples in Module :mod:`plugs` how to use this decorator / function 

:param plugin: :param name: :param package: :param replace: :param auto_tag: :return: 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L454"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `tag`

```python
tag(func: Callable) → Callable
```

Method decorator for tagging a method as callable through the plugs interface 

Note that the instantiated class must still be registered as plugin object (either with the class decorator or dynamically) 

:param func: function to decorate :return: the function 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L471"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `initialize`

```python
initialize(func: Callable) → Callable
```

Decorator for functions that shall be called by the plugs package directly after the module is loaded 

:param func: Function to decorate :return: The function itself 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L487"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `finalize`

```python
finalize(func: Callable) → Callable
```

Decorator for functions that shall be called by the plugs package directly after ALL modules are loaded 

:param func: Function to decorate :return: The function itself 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L503"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `atexit`

```python
atexit(func: Callable[[int], Any]) → Callable[[int], Any]
```

Decorator for functions that shall be called by the plugs package directly after at exit of program. 

.. important:: There is no automatism as in atexit.atexit. The function plugs.shutdown() must be explicitly called  during the shutdown procedure of your program. This is by design, so you can choose the exact situation in your  shutdown handler. 

The atexit-functions are called with a single integer argument, which is passed down from plugin.exit(int) It is intended for passing down the signal number that initiated the program termination 

:param func: Function to decorate :return: The function itself 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L526"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `load`

```python
load(package: str, load_as: Optional[str] = None, prefix: Optional[str] = None)
```

Loads a python package as plugin package 

Executes a regular python package load. That means a potentially existing __init__.py is executed. Decorator @register can by used to register functions / classes / class istances as plugin callable Decorator @initializer can be used to tag functions that shall be called after package loading Decorator @finalizer can be used to tag functions that shall be called after ALL plugin packges have been loaded Instead of using @initializer, you may of course use __init__.py 

Python packages may be loaded under a different plugs package name. Python packages must be unique and the name under which they are loaded as plugin package also. 

:param package: Python package to load as plugin package :param load_as: Plugin package registration name. If None the name is the python's package simple name :param prefix: Prefix to python package to create fully qualified name. This is used only to locate the python package  and ignored otherwise. Useful if all the plugin module are in a dedicated folder :return: 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L582"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `load_all_named`

```python
load_all_named(
    packages_named: Mapping[str, str],
    prefix: Optional[str] = None,
    ignore_errors=False
)
```

Load all packages in packages_named with mapped names 

:param packages_named: Dict[load_as, package] 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L599"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `load_all_unnamed`

```python
load_all_unnamed(
    packages_unnamed: Iterable[str],
    prefix: Optional[str] = None,
    ignore_errors=False
)
```

Load all packages in packages_unnamed with default names 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L613"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `load_all_finalize`

```python
load_all_finalize(ignore_errors=False)
```

Calls all functions registered with @finalize from all loaded modules in the order they were loaded 

This must be executed after the last plugin package is loaded 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L636"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `close_down`

```python
close_down(**kwargs) → Any
```

Calls all functions registered with @atexit from all loaded modules in reverse order of module load order 

Modules are processed in reverse order. Several at-exit tagged functions of a single module are processed in the order of registration. 

Errors raised in functions are suppressed to ensure all plugins are processed :return: 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L660"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `dereference`

```python
dereference(
    package: str,
    plugin: str,
    method: Optional[str] = None,
    args=None,
    kwargs=None
)
```






---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L710"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `call`

```python
call(
    package: str,
    plugin: str,
    method: Optional[str] = None,
    args=(),
    kwargs=None,
    as_thread: bool = False,
    thread_name: Optional[str] = None
) → Any
```

Call a function/method from the loaded plugins 

If a plugin is a function or a callable instance of a class, this is equivalent to 

``package.plugin(*args, **kwargs)`` 

If plugin is a class instance from which a method is called, this is equivalent to the followig. Also remember, that method must have the attribute ``plugin_callable = True`` 

``package.plugin.method(*args, **kwargs)`` 

Calls are serialized by a thread lock. The thread lock is shared with call_ignore_errors. 

.. note:
```      There is no logger in this function as they all belong up-level where the exceptions are handled.      If you want logger messages instead of exceptions, use :func:`call_ignore_errors` 

```
:param package: Name of the plugin package in which to look for function/class instance :param plugin: Function name or instance name of a class :param method: Method name when accessing a class instance' method. Leave at *None* if unneeded. :param as_thread: Run the callable in separate daemon thread.  There is no return value from the callable in this case! The return value is the thread object.  Also note that Exceptions in the Thread must be handled in the Thread and are not propagated to the main Thread.  All threads are started as daemon threads with terminate upon main program termination.  There is not stop-thread mechanism. This is intended for short lived threads. :param thread_name: Name of the thread :param args: Arguments passed to callable :param kwargs: Keyword arguments passed to callable :return: The return value from the called function, or, if started as thread the thread object 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L748"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `call_ignore_errors`

```python
call_ignore_errors(
    package: str,
    plugin: str,
    method: Optional[str] = None,
    args=(),
    kwargs=None,
    as_thread: bool = False,
    thread_name: Optional[str] = None
) → Any
```

Call a function/method from the loaded plugins ignoring all raised Exceptions. 

Errors get logged. 

See :func:`call` for parameter documentation. 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L773"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `exists`

```python
exists(
    package: str,
    plugin: Optional[str] = None,
    method: Optional[str] = None
) → bool
```

Check if an object is registered within the plugs package 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L787"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get`

```python
get(
    package: str,
    plugin: Optional[str] = None,
    method: Optional[str] = None
) → Any
```

Get a plugs-package registered object 

The return object depends on the number of parameters 

* 1 argument: Get the python module reference for the plugs *package* * 2 arguments: Get the plugin reference for the plugs *package.plugin* * 3 arguments: Get the plugin reference for the plugs *package.plugin.method* 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L816"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `loaded_as`

```python
loaded_as(module_name: str) → str
```

Return the plugin name a python module is loaded as 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L824"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `delete`

```python
delete(package: str, plugin: Optional[str] = None, ignore_errors=False)
```

Delete a plugin object from the registered plugs callables 

Note: This does not 'unload' the python module. It merely makes it un-callable via plugs! 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L840"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `dump_plugins`

```python
dump_plugins(stream)
```

Write a human readable summary of all plugin callables to stream 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L869"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `summarize`

```python
summarize()
```

Create a reference summary of all plugin callables in dictionary format 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L907"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_help_rst`

```python
generate_help_rst(stream)
```

Write a reference of all plugin callables in Restructured Text format 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L963"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_all_loaded_packages`

```python
get_all_loaded_packages() → Dict[str, str]
```

Report a short summary of all loaded packages 

:return: Dictionary of the form `{loaded_as: loaded_from, ...}` 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L971"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_all_failed_packages`

```python
get_all_failed_packages() → Dict[str, str]
```

Report those packages that did not load error free 

.. note:: Package could fail to load 

 1. altogether: these package are not registered  2. partially: during initializer, finalizer functions: The package is loaded,  but the function did not execute error-free 

 Partially loaded packages are listed in both _PLUGINS and _PLUGINS_FAILED 

:return: Dictionary of the form `{loaded_as: loaded_from, ...}` 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PluginPackageClass`
A local data class for holding all information about a loaded plugin package 

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/jukebox/plugs.py#L143"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(loaded_from: str)
```






---

#### <kbd>property</kbd> atexit





---

#### <kbd>property</kbd> finalizer





---

#### <kbd>property</kbd> initializer





---

#### <kbd>property</kbd> loaded_from





---

#### <kbd>property</kbd> module





---

#### <kbd>property</kbd> plugins










---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
