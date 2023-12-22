<!-- markdownlint-disable -->

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/callingback.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `jukebox.callingback`
Provides a generic callback handler 



---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/callingback.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `CallbackHandler`
Generic Callback Handler to collect callbacks functions through :func:`register` and execute them with :func:`run_callbacks` 

A lock is used to sequence registering of new functions and running callbacks. 

:param name: A name of this handler for usage in log messages :param logger: The logger instance to use for logging :param context: A custom context handler to use as lock. If none, a local :class:`threading.Lock()` will be created 

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/callingback.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(name: str, logger: Logger, context=None)
```






---

#### <kbd>property</kbd> has_callbacks

:data:`True` if there are any registered callbacks. Read-only property 



---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/callingback.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `register`

```python
register(func: Optional[Callable[, NoneType]])
```

Register a new function to be executed when the callback event happens 

:param func: The function to register. If set to :data:`None`, this register request is silently ignored. 

---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/callingback.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_callbacks`

```python
run_callbacks(*args, **kwargs)
```

Run all registered callbacks. 

*ALL* exceptions from callback functions will be caught and logged only. Exceptions are not raised upwards!  




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
