<!-- markdownlint-disable -->

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `jukebox.utils`
Common utility functions 

**Global Variables**
---------------
- **cmd_alias_definitions**

---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/utils.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `decode_rpc_call`

```python
decode_rpc_call(cfg_rpc_call: Dict) → Optional[Dict]
```

Makes sure that the core rpc call parameters have valid default values in cfg_rpc_call. 

.. important: Leaves all other parameters in cfg_action untouched or later downstream processing! 

:param cfg_rpc_call: RPC command as configuration entry :return: A fully populated deep copy of cfg_rpc_call 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/utils.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `decode_rpc_command`

```python
decode_rpc_command(
    cfg_rpc_cmd: Dict,
    logger: Logger = <Logger jb.utils (WARNING)>
) → Optional[Dict]
```

Decode an RPC Command from a config entry. 

This means 

 * Decode RPC command alias (if present)  * Ensure all RPC call parameters have valid default values 

If the command alias cannot be decoded correctly, the command is mapped to misc.empty_rpc_call which emits a misuse warning when called If an explicitly specified this is not done. However, it is ensured that the returned dictionary contains all mandatory parameters for an RPC call. RPC call functions have error handling for non-existing RPC commands and we get a clearer error message. 

:param cfg_rpc_cmd: RPC command as configuration entry :param logger: The logger to use :return: A decoded, fully populated deep copy of cfg_rpc_cmd 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/utils.py#L94"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `decode_and_call_rpc_command`

```python
decode_and_call_rpc_command(
    rpc_cmd: Dict,
    logger: Logger = <Logger jb.utils (WARNING)>
)
```

Convenience function combining decode_rpc_command and plugs.call_ignore_errors 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/utils.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `bind_rpc_command`

```python
bind_rpc_command(
    cfg_rpc_cmd: Dict,
    dereference=False,
    logger: Logger = <Logger jb.utils (WARNING)>
)
```

Decode an RPC command configuration entry and bind it to a function 

:param dereference: Dereference even the call to plugs.call(...) 

 #. If false, the returned function is ``plugs.call(package, plugin, method, *args, **kwargs)`` with  all checks applied at bind time  #. If true, the returned function is ``package.plugin.method(*args, **kwargs)`` with  all checks applied at bind time. 

 Setting deference to True, circumvents the dynamic nature of the plugins: the function to call  must exist at bind time and cannot change. If False, the function to call must only exist at call time.  This can be important during the initialization where package ordering and initialization means that not all  classes have been instantiated yet. With dereference=True also the plugs thread lock for serialization of calls  is circumvented. Use with care! 

:return: Callable function w/o parameters which directly runs the RPC command  using plugs.call_ignore_errors 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/utils.py#L144"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `rpc_call_to_str`

```python
rpc_call_to_str(cfg_rpc_call: Dict, with_args=True) → str
```

Return a readable string of an RPC call config 

:param cfg_rpc_call: RPC call configuration entry :param with_args: Return string shall include the arguments of the function 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/utils.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `indent`

```python
indent(doc, spaces=4)
```






---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/utils.py#L192"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_cmd_alias_rst`

```python
generate_cmd_alias_rst(stream)
```

Write a reference of all rpc command aliases in Restructured Text format 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/utils.py#L231"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_cmd_alias_reference`

```python
generate_cmd_alias_reference(stream)
```

Write a reference of all rpc command aliases in text format 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/jukebox/utils.py#L267"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_git_state`

```python
get_git_state()
```

Return git state information for the current branch 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
