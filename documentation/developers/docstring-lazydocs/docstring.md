<!-- markdownlint-disable -->

# API Overview

## Modules

- [`components`](./components.md#module-components)
- [`components.battery_monitor`](./components.battery_monitor.md#module-componentsbattery_monitor)
- [`components.controls`](./components.controls.md#module-componentscontrols)
- [`components.rfid`](./components.rfid.md#module-componentsrfid)
- [`components.rfid.readerbase`](./components.rfid.readerbase.md#module-componentsrfidreaderbase)
- [`components.rpc_command_alias`](./components.rpc_command_alias.md#module-componentsrpc_command_alias): This file provides definitions for RPC command aliases
- [`components.synchronisation`](./components.synchronisation.md#module-componentssynchronisation)
- [`components.synchronisation.syncutils`](./components.synchronisation.syncutils.md#module-componentssynchronisationsyncutils)
- [`jukebox`](./jukebox.md#module-jukebox)
- [`jukebox.NvManager`](./jukebox.NvManager.md#module-jukeboxnvmanager)
- [`jukebox.callingback`](./jukebox.callingback.md#module-jukeboxcallingback): Provides a generic callback handler
- [`jukebox.playlistgenerator`](./jukebox.playlistgenerator.md#module-jukeboxplaylistgenerator): Playlists are build from directory content in the following way:
- [`jukebox.plugs`](./jukebox.plugs.md#module-jukeboxplugs): A plugin package with some special functionality
- [`jukebox.rpc`](./jukebox.rpc.md#module-jukeboxrpc)
- [`jukebox.utils`](./jukebox.utils.md#module-jukeboxutils): Common utility functions
- [`jukebox.version`](./jukebox.version.md#module-jukeboxversion)
- [`misc`](./misc.md#module-misc)
- [`misc.inputminus`](./misc.inputminus.md#module-miscinputminus): Zero 3rd-party dependency module for user prompting
- [`misc.simplecolors`](./misc.simplecolors.md#module-miscsimplecolors): Zero 3rd-party dependency module to add colors to unix terminal output

## Classes

- [`readerbase.ReaderBaseClass`](./components.rfid.readerbase.md#class-readerbaseclass): Abstract Base Class for all Reader Classes to ensure common API
- [`NvManager.nv_dict`](./jukebox.NvManager.md#class-nv_dict)
- [`NvManager.nv_manager`](./jukebox.NvManager.md#class-nv_manager)
- [`callingback.CallbackHandler`](./jukebox.callingback.md#class-callbackhandler): Generic Callback Handler to collect callbacks functions through :func:`register` and execute them
- [`playlistgenerator.PlaylistCollector`](./jukebox.playlistgenerator.md#class-playlistcollector): Build a playlist from directory(s)
- [`playlistgenerator.PlaylistEntry`](./jukebox.playlistgenerator.md#class-playlistentry)
- [`plugs.PluginPackageClass`](./jukebox.plugs.md#class-pluginpackageclass): A local data class for holding all information about a loaded plugin package
- [`simplecolors.Colors`](./misc.simplecolors.md#class-colors): Container class for all the colors as constants

## Functions

- [`syncutils.clean_foldername`](./components.synchronisation.syncutils.md#function-clean_foldername)
- [`syncutils.ensure_trailing_slash`](./components.synchronisation.syncutils.md#function-ensure_trailing_slash)
- [`syncutils.remove_leading_slash`](./components.synchronisation.syncutils.md#function-remove_leading_slash)
- [`syncutils.remove_trailing_slash`](./components.synchronisation.syncutils.md#function-remove_trailing_slash)
- [`playlistgenerator.decode_livestream`](./jukebox.playlistgenerator.md#function-decode_livestream)
- [`playlistgenerator.decode_m3u`](./jukebox.playlistgenerator.md#function-decode_m3u)
- [`playlistgenerator.decode_musicfile`](./jukebox.playlistgenerator.md#function-decode_musicfile)
- [`playlistgenerator.decode_podcast`](./jukebox.playlistgenerator.md#function-decode_podcast)
- [`playlistgenerator.decode_podcast_core`](./jukebox.playlistgenerator.md#function-decode_podcast_core)
- [`plugs.atexit`](./jukebox.plugs.md#function-atexit): Decorator for functions that shall be called by the plugs package directly after at exit of program.
- [`plugs.call`](./jukebox.plugs.md#function-call): Call a function/method from the loaded plugins
- [`plugs.call_ignore_errors`](./jukebox.plugs.md#function-call_ignore_errors): Call a function/method from the loaded plugins ignoring all raised Exceptions.
- [`plugs.close_down`](./jukebox.plugs.md#function-close_down): Calls all functions registered with @atexit from all loaded modules in reverse order of module load order
- [`plugs.delete`](./jukebox.plugs.md#function-delete): Delete a plugin object from the registered plugs callables
- [`plugs.dereference`](./jukebox.plugs.md#function-dereference)
- [`plugs.dump_plugins`](./jukebox.plugs.md#function-dump_plugins): Write a human readable summary of all plugin callables to stream
- [`plugs.exists`](./jukebox.plugs.md#function-exists): Check if an object is registered within the plugs package
- [`plugs.finalize`](./jukebox.plugs.md#function-finalize): Decorator for functions that shall be called by the plugs package directly after ALL modules are loaded
- [`plugs.generate_help_rst`](./jukebox.plugs.md#function-generate_help_rst): Write a reference of all plugin callables in Restructured Text format
- [`plugs.get`](./jukebox.plugs.md#function-get): Get a plugs-package registered object
- [`plugs.get_all_failed_packages`](./jukebox.plugs.md#function-get_all_failed_packages): Report those packages that did not load error free
- [`plugs.get_all_loaded_packages`](./jukebox.plugs.md#function-get_all_loaded_packages): Report a short summary of all loaded packages
- [`plugs.initialize`](./jukebox.plugs.md#function-initialize): Decorator for functions that shall be called by the plugs package directly after the module is loaded
- [`plugs.load`](./jukebox.plugs.md#function-load): Loads a python package as plugin package
- [`plugs.load_all_finalize`](./jukebox.plugs.md#function-load_all_finalize): Calls all functions registered with @finalize from all loaded modules in the order they were loaded
- [`plugs.load_all_named`](./jukebox.plugs.md#function-load_all_named): Load all packages in packages_named with mapped names
- [`plugs.load_all_unnamed`](./jukebox.plugs.md#function-load_all_unnamed): Load all packages in packages_unnamed with default names
- [`plugs.loaded_as`](./jukebox.plugs.md#function-loaded_as): Return the plugin name a python module is loaded as
- [`plugs.register`](./jukebox.plugs.md#function-register): A generic decorator / run-time function to register plugin module callables
- [`plugs.summarize`](./jukebox.plugs.md#function-summarize): Create a reference summary of all plugin callables in dictionary format
- [`plugs.tag`](./jukebox.plugs.md#function-tag): Method decorator for tagging a method as callable through the plugs interface
- [`utils.bind_rpc_command`](./jukebox.utils.md#function-bind_rpc_command): Decode an RPC command configuration entry and bind it to a function
- [`utils.decode_and_call_rpc_command`](./jukebox.utils.md#function-decode_and_call_rpc_command): Convenience function combining decode_rpc_command and plugs.call_ignore_errors
- [`utils.decode_rpc_call`](./jukebox.utils.md#function-decode_rpc_call): Makes sure that the core rpc call parameters have valid default values in cfg_rpc_call.
- [`utils.decode_rpc_command`](./jukebox.utils.md#function-decode_rpc_command): Decode an RPC Command from a config entry.
- [`utils.generate_cmd_alias_reference`](./jukebox.utils.md#function-generate_cmd_alias_reference): Write a reference of all rpc command aliases in text format
- [`utils.generate_cmd_alias_rst`](./jukebox.utils.md#function-generate_cmd_alias_rst): Write a reference of all rpc command aliases in Restructured Text format
- [`utils.get_git_state`](./jukebox.utils.md#function-get_git_state): Return git state information for the current branch
- [`utils.indent`](./jukebox.utils.md#function-indent)
- [`utils.rpc_call_to_str`](./jukebox.utils.md#function-rpc_call_to_str): Return a readable string of an RPC call config
- [`version.version`](./jukebox.version.md#function-version): Return the Jukebox version as a string
- [`version.version_info`](./jukebox.version.md#function-version_info): Return the Jukebox version as a tuple of three numbers
- [`misc.flatten`](./misc.md#function-flatten): Flatten all levels of hierarchy in nested iterables
- [`misc.getattr_hierarchical`](./misc.md#function-getattr_hierarchical): Like the builtin getattr, but descends though the hierarchy levels
- [`misc.recursive_chmod`](./misc.md#function-recursive_chmod): Recursively change folder and file permissions
- [`inputminus.input_int`](./misc.inputminus.md#function-input_int): Request an integer input from user
- [`inputminus.input_yesno`](./misc.inputminus.md#function-input_yesno): Request a yes / no choice from user
- [`inputminus.msg_highlight`](./misc.inputminus.md#function-msg_highlight)
- [`simplecolors.print`](./misc.simplecolors.md#function-print): Drop-in replacement for print with color choice and auto color reset for convenience
- [`simplecolors.resolve`](./misc.simplecolors.md#function-resolve): Resolve a color name into the respective color constant


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
