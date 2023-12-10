# Jukebox Apps

The Jukebox\'s core apps are located in `src/jukebox`. Run the following
command to learn more about each app and its parameters:

``` bash
$ cd src/jukebox
$ ./<scriptname> -h
```


## Jukebox Core

**Scriptname:** [run_jukebox.py](../../src/jukebox/run_jukebox.py)

This is the main app and starts the Jukebox Core.

Usually this runs as a service, which is started automatically after boot-up. At times, it may be necessary to restart the service. For example after a configuration change. Not all configuration changes can be applied on-the-fly. See [Jukebox Configuration](../builders/configuration.md#jukebox-configuration).

For debugging, it is usually desirable to run the Jukebox directly from the console rather than as service. This gives direct logging info in the console and allows changing command line parameters. See [Troubleshooting](../builders/troubleshooting.md).


## Configuration Tools

Before running the configuration tools, stop the Jukebox Core service.
See [Best practice procedure](../builders/configuration.md#best-practice-procedure).

### Audio

**Scriptname:** [run_configure_audio.py](../../src/jukebox/run_configure_audio.py)

Setup tool to register the PulseAudio sinks as primary and secondary audio outputs. 

Will also setup equalizer and mono down mixer in the pulseaudio config file. Run this once after installation. Can be re-run at any time to change the settings. For more information see [Audio Configuration](../builders/audio.md).

### RFID Reader

**Scriptname:** [run_register_rfid_reader.py](../../src/jukebox/run_register_rfid_reader.py)

Setup tool to configure the RFID Readers. 

Run this once to register and configure the RFID readers with the Jukebox. Can be re-run at any time to change the settings. For more information see [RFID Readers](./rfid/README.md).

> [!NOTE]
> This tool will always write a new configurations file. Thus, overwrite the old one (after checking with the user). Any manual modifications to the settings will have to be re-applied


## Developer Tools

### RPC

**Scriptname:** [run_rpc_tool.py](../../src/jukebox/run_rpc_tool.py)

Command Line Interface to the Jukebox RPC Server. 

A command line tool for sending RPC commands to the running jukebox app. This uses the same interface as the WebUI. Can be used for additional control or for debugging.The tool features auto-completion and command history. The list of available commands is fetched from the running Jukebox service.

### Publicity Sniffer

**Scriptname:** [run_publicity_sniffer.py](../../src/jukebox/run_publicity_sniffer.py)

A command line tool that monitors all messages being sent out from the Jukebox via the publishing interface. Received messages are printed in the console. Mainly used for debugging.
