"""
Common utility functions
"""
import functools
import logging
import copy
import subprocess
from typing import (Dict, Optional)
from components.rpc_command_alias import cmd_alias_definitions
import inspect
import jukebox.plugs as plugs


log = logging.getLogger('jb.utils')


def decode_rpc_call(cfg_rpc_call: Dict) -> Optional[Dict]:
    """Makes sure that the core rpc call parameters have valid default values in cfg_rpc_call.

    > [!IMPORTANT]
    > Leaves all other parameters in cfg_action untouched or later downstream processing!

    :param cfg_rpc_call: RPC command as configuration entry
    :return: A fully populated deep copy of cfg_rpc_call
    """
    if cfg_rpc_call is None:
        return None
    # We need a deep copy here, since we do not want to modify the source
    # The source could have unset keys on purpose, or be an (incomplete) template for different RPC actions
    ret_action = copy.deepcopy(cfg_rpc_call)
    ret_action.setdefault('package', 'package_not_specified')
    ret_action.setdefault('plugin', 'plugin_not_specified'),
    ret_action.setdefault('method', None),
    ret_action.setdefault('args', None),
    ret_action.setdefault('kwargs', None)
    return ret_action


def decode_rpc_command(cfg_rpc_cmd: Dict, logger: logging.Logger = log) -> Optional[Dict]:
    """
    Decode an RPC Command from a config entry.

    This means

    * Decode RPC command alias (if present)
    * Ensure all RPC call parameters have valid default values

    If the command alias cannot be decoded correctly, the command is mapped to misc.empty_rpc_call
    which emits a misuse warning when called
    If an explicitly specified this is not done. However, it is ensured that the returned
    dictionary contains all mandatory parameters for an RPC call. RPC call functions have error handling
    for non-existing RPC commands and we get a clearer error message.

    :param cfg_rpc_cmd: RPC command as configuration entry
    :param logger: The logger to use
    :return: A decoded, fully populated deep copy of cfg_rpc_cmd
    """
    # Action entry does not exist
    if cfg_rpc_cmd is None:
        return None
    # Alias selection is not present: assume regular rpc call data format
    if 'alias' not in cfg_rpc_cmd:
        alias = 'custom'
    else:
        alias = cfg_rpc_cmd.get('alias', 'none')
        # Alias is 'None', i.e. keyword is present but empty -> treat as 'none'
        if alias is None:
            alias = 'none'

    # Check validity of alias
    valid = [*cmd_alias_definitions.keys(), 'none', 'custom']
    if alias not in valid:
        logger.error(f"Invalid rpc command alias: '{alias}'! Must be one of "
                     f"{valid}. Default to 'none'.")
        return {'package': 'misc', 'plugin': 'empty_rpc_call', 'method': None, 'kwargs': None,
                'args': f"Invalid rpc command alias '{alias}' has been mapped to 'misc.empty_rpc_call()'"}

    if alias == 'none':
        return {'package': 'misc', 'plugin': 'empty_rpc_call',
                'method': None, 'args': None, 'kwargs': None}

    if alias == 'custom':
        return decode_rpc_call(cfg_rpc_cmd)

    # True RPC command
    action = decode_rpc_call(cmd_alias_definitions[alias])
    # Possible override args / kwargs
    if 'args' in cfg_rpc_cmd:
        action['args'] = cfg_rpc_cmd['args']
    if 'kwargs' in cfg_rpc_cmd:
        action['kwargs'] = cfg_rpc_cmd['kwargs']
    return action


def decode_and_call_rpc_command(rpc_cmd: Dict, logger: logging.Logger = log):
    """Convenience function combining decode_rpc_command and plugs.call_ignore_errors"""
    action = decode_rpc_command(rpc_cmd, logger)
    if action is not None:
        res = plugs.call_ignore_errors(action['package'], action['plugin'],
                                       action['method'], args=action['args'], kwargs=action['kwargs'])
    else:
        res = None
    return res


def bind_rpc_command(cfg_rpc_cmd: Dict, dereference=False, logger: logging.Logger = log):
    """Decode an RPC command configuration entry and bind it to a function

    :param dereference: Dereference even the call to plugs.call(...)

            #. If false, the returned function is ``plugs.call(package, plugin, method, *args, **kwargs)`` with
                all checks applied at bind time
            #. If true, the returned function is ``package.plugin.method(*args, **kwargs)`` with
                all checks applied at bind time.

        Setting deference to True, circumvents the dynamic nature of the plugins: the function to call
            must exist at bind time and cannot change. If False, the function to call must only exist at call time.
            This can be important during the initialization where package ordering and initialization means that not all
            classes have been instantiated yet. With dereference=True also the plugs thread lock for serialization of calls
            is circumvented. Use with care!

    :return: Callable function w/o parameters which directly runs the RPC command
        using plugs.call_ignore_errors"""
    action = decode_rpc_command(cfg_rpc_cmd, logger)
    if action is None:
        raise KeyError(f"RPC command config is empty: '{cfg_rpc_cmd}'")

    if dereference:
        func, args, kwargs = plugs.dereference(action['package'],
                                               action['plugin'],
                                               action['method'],
                                               args=action['args'],
                                               kwargs=action['kwargs'])

        return functools.partial(func, *args, **kwargs)
    else:
        return functools.partial(plugs.call_ignore_errors,
                                 action['package'],
                                 action['plugin'],
                                 action['method'],
                                 args=action['args'],
                                 kwargs=action['kwargs'])


def rpc_call_to_str(cfg_rpc_call: Dict, with_args=True) -> str:
    """Return a readable string of an RPC call config

    :param cfg_rpc_call: RPC call configuration entry
    :param with_args: Return string shall include the arguments of the function
    """
    package = cfg_rpc_call.get('package', '?')
    plugin = cfg_rpc_call.get('plugin', '?')
    method = cfg_rpc_call.get('method', None)
    args = cfg_rpc_call.get('args', None)
    kwargs = cfg_rpc_call.get('kwargs', None)

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
                args_str = ", ".join([f"'{x}'" if isinstance(x, str) else str(x) for x in args])
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


def get_config_action(cfg, section, option, default, valid_actions_dict, logger):
    """
    Looks up the given {section}.{option} config option and returns
    the associated entry from valid_actions_dict, if valid. Falls back to the given
    default otherwise.
    """
    action = cfg.setndefault(section, option, value='').lower()
    if action not in valid_actions_dict:
        logger.error(f"Config {section}.{option} must be one of {valid_actions_dict.keys()}. Using default '{default}'")
        action = default
    return valid_actions_dict[action]


def indent(doc, spaces=4):
    lines = doc.split('\n')
    for i in range(0, len(lines)):
        lines[i] = " " * spaces + lines[i]
    return "\n".join(lines)


def generate_cmd_alias_rst(stream):
    """Write a reference of all rpc command aliases in Restructured Text format"""
    print("RPC Command Alias Reference", file=stream)
    print("***************************\n\n", file=stream)
    print(".. |--| unicode:: U+2014", file=stream)
    print(".. |->| unicode:: U+21d2\n", file=stream)

    # 'play_card':
    #    Executes   : player.ctrl.play_card()
    #    Signature  : player.ctrl.play_card(folder=None)
    #    Description: Main entry point for trigger music playing from RFID reader
    for cmd, action in cmd_alias_definitions.items():
        try:
            func = plugs.get(action['package'], action['plugin'], action.get('method', None))
        except Exception as e:
            description = f"ERROR: {e.__class__.__name__}: {e}"
            signature = "(---UNKNOWN---)"
        else:
            description = inspect.cleandoc(func.__doc__ or "")
            signature = inspect.signature(func)
        calls = rpc_call_to_str(action, with_args=False)

        print(f".. py:function:: {cmd}(...) -> {calls}{signature}", file=stream)
        print("    :noindex:\n", file=stream)
        if 'title' in action:
            print(f"    **{action['title']}**\n", file=stream)
        print(f"{indent(description, 4)}\n", file=stream)
        if 'note' in action:
            print(f"    .. note:: {action['note']}\n", file=stream)
        modifiers = filter(lambda k: k not in ['package', 'plugin', 'method', 'title', 'args', 'kwargs', 'note'],
                           action.keys())
        modifiers_exist = False
        for m in modifiers:
            if not modifiers_exist:
                print("    Default actions modifiers", file=stream)
                modifiers_exist = True
            print(f"         **{m}** |--| {action[m]}\n", file=stream)


def generate_cmd_alias_reference(stream):
    """Write a reference of all rpc command aliases in text format"""
    width = 127
    print('*' * width, file=stream)
    print("RPC command alias definitions", file=stream)
    print('*' * width, file=stream)
    print("\n", file=stream)
    for cmd, action in cmd_alias_definitions.items():
        try:
            func = plugs.get(action['package'], action['plugin'], action.get('method', None))
        except Exception as e:
            description = f"ERROR: {e.__class__.__name__}: {e}"
            signature = "(---UNKNOWN---)"
        else:
            description = (func.__doc__ or "").split('\n\n', 1)[0].strip('\n ')
            signature = inspect.signature(func)
        readable = rpc_call_to_str(action, with_args=True)
        print(f"'{cmd}':", file=stream)
        print(f"   Executes   : {readable}", file=stream)
        print(f"   Signature  : {rpc_call_to_str(action, with_args=False)}{signature}", file=stream)
        modifiers = filter(lambda k: k not in ['package', 'plugin', 'method', 'title', 'args', 'kwargs', 'note'],
                           action.keys())
        modifiers_exist = False
        for m in modifiers:
            if not modifiers_exist:
                print("   Default actions modifiers", file=stream)
                modifiers_exist = True
            print(f"        {m} -- {action[m]}", file=stream)
        if 'title' in action:
            print(f"   Title      : {action['title']}", file=stream)
        print(f"   Description: {description}", file=stream)
        if 'note' in action:
            print(f"   Note       : {action['note']}\n", file=stream)
    print('*' * width, file=stream)


def get_git_state():
    """Return git state information for the current branch"""

    gitlog = "No git log info"
    try:
        sub = subprocess.run("git log --pretty='%h [%cs] %s %d' -n 1 --no-color",
                             shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             check=True)
        gitlog = sub.stdout.decode('utf-8').strip()
    except Exception as e:
        log.error(f"{e.__class__.__name__}: {e}")

    describe = "No git describe info"
    try:
        sub = subprocess.run("git describe --tag --dirty='-dirty'",
                             shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             check=True)
        if sub.returncode == 0:
            describe = sub.stdout.decode('utf-8').strip()
    except Exception as e:
        log.error(f"{e.__class__.__name__}: {e}")

    return f"{gitlog} [{describe}]"
