"""
Miscellaneous function package
"""
import jukebox.plugs as plugin


@plugin.register
def rpc_cmd_help():
    return plugin.summarize()


@plugin.register
def get_all_loaded_packages():
    return plugin.get_all_loaded_packages()


@plugin.register
def get_all_failed_packages():
    return plugin.get_all_failed_packages()
