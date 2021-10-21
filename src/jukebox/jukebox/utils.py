import logging
import copy
import subprocess
from typing import (Dict, Mapping)


log = logging.getLogger('jb.utils')


def decode_rpc_call(cfg_action: Dict):
    """Makes sure that rpc call parameters have valid default values

    Important: Leaves all other parameters in cfg_action untouched or later downstream processing!"""
    if cfg_action is None:
        return None
    # We need a deep copy here, since we do not want to modify the source
    # The source could have unset keys on purpose, or be an (incomplete) template for different RPC actions
    ret_action = copy.deepcopy(cfg_action)
    ret_action.setdefault('package', 'package_not_specified')
    ret_action.setdefault('plugin', 'plugin_not_specified'),
    ret_action.setdefault('method', None),
    ret_action.setdefault('args', None),
    ret_action.setdefault('kwargs', None)
    return ret_action


def decode_action(cfg_action, quick_select_dict=None, logger=log):
    # Action entry does not exist
    if cfg_action is None:
        return None
    # Quick selection is not present: assume regular rpc call data format
    if 'quick_select' not in cfg_action:
        return decode_rpc_call(cfg_action)
    qs = cfg_action.get('quick_select', None)
    # Quick selection is 'None', i.e. keyword is present but empty -> treat as 'none'
    if qs is None:
        qs = 'none'
    # Check validity of quick selection
    valid = [*quick_select_dict.keys(), 'none', 'custom']
    if qs not in valid:
        logger.error(f"Action configuration of 'quick_select: {qs}' must be one of"
                     f"{valid}. Default to 'none'.")
    if qs == 'none':
        return None
    if qs == 'custom':
        return decode_rpc_call(cfg_action)
    # True quick select action
    action = decode_rpc_call(quick_select_dict[qs])
    # Possible override args / kwargs
    if 'args' in cfg_action:
        action['args'] = cfg_action['args']
    if 'kwargs' in cfg_action:
        action['kwargs'] = cfg_action['kwargs']
    return action


def action_to_str(action: Mapping, with_args=True) -> str:
    package = action.get('package', '?')
    plugin = action.get('plugin', '?')
    method = action.get('method', None)
    args = action.get('args', None)
    kwargs = action.get('kwargs', None)

    method_str = ''
    args_str = ''
    kwargs_str = ''
    separator = ''
    if method is not None:
        method_str = f".{method}"
    if args is not None:
        # args should an argument list, but these cases are specially handled in plugs.py
        # to make things more user friendly
        # - if a single argument is passed, wrap is in a list first
        # - if a string is passed, it is iterable but a single argument
        if isinstance(args, str):
            args_str = args
        else:
            try:
                args_str = ", ".join([f"'{x}'" if type(x) == str else str(x) for x in args])
            except TypeError:
                args_str = f"{args}"
    if kwargs is not None:
        kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        if args is not None:
            separator = ", "
    if with_args:
        readable = f"{package}.{plugin}{method_str}({args_str}{separator}{kwargs_str})"
    else:
        readable = f"{package}.{plugin}{method_str}"
    return readable


def get_git_state():
    """Return git state information for the current branch"""
    try:
        sub = subprocess.run("git log --pretty='%h [%cs] %s %d' -n 1 --no-color",
                             shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             check=True)
        gitlog = sub.stdout.decode('utf-8').strip()
    except Exception as e:
        log.error(f"{e.__class__.__name__}: {e}")
        gitlog = "Unable to get git log"

    try:
        sub = subprocess.run("git describe --tag --dirty='-dirty'",
                             shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             check=True)
        describe = sub.stdout.decode('utf-8').strip()
    except Exception as e:
        log.error(f"{e.__class__.__name__}: {e}")
        describe = "Unable to get git describe"

    return f"{gitlog} [{describe}]"
