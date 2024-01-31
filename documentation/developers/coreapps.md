# Jukebox Apps

The Jukebox\'s core apps are located in `src/jukebox`. Run the following
command to learn more about each app and its parameters:

``` bash
$ cd src/jukebox
$ ./<scriptname> -h
```

## Jukebox Core

**Scriptname:** [run_jukebox.sh](../../run_jukebox.sh)

This is the main app and starts the Jukebox Core.

Usually this runs as a service, which is started automatically after boot-up. At times, it may be necessary to restart the service. For example after a configuration change. Not all configuration changes can be applied on-the-fly. See [Jukebox Configuration](../builders/configuration.md#jukebox-configuration).

For debugging, it is usually desirable to run the Jukebox directly from the console rather than as service. This gives direct logging info in the console and allows changing command line parameters. See [Troubleshooting](../builders/troubleshooting.md).

## Configuration Tools

Before running the configuration tools, stop the Jukebox Core service.
See [Best practice procedure](../builders/configuration.md#best-practice-procedure).

### Audio

**Scriptname:** [setup_audio_sink.sh](../../installation/components/setup_audio_sink.sh)

Setup tool to register the PulseAudio sinks as primary and secondary audio outputs.

Will also setup equalizer and mono down mixer in the pulseaudio config file. Run this once after installation. Can be re-run at any time to change the settings. For more information see [Audio Configuration](../builders/audio.md).

### RFID Reader

**Scriptname:** [setup_rfid_reader.sh](../../installation/components/setup_rfid_reader.sh)

Setup tool to configure the RFID Readers.

Run this once to register and configure the RFID readers with the Jukebox. Can be re-run at any time to change the settings. For more information see [RFID Readers](./rfid/README.md).

> [!NOTE]
> This tool will always write a new configurations file. Thus, overwrite the old one (after checking with the user). Any manual modifications to the settings will have to be re-applied

## Developer Tools

### RPC

**Scriptname:** [run_rpc_tool.sh](../../tools/run_rpc_tool.sh)

Command Line Interface to the Jukebox RPC Server.

A command line tool for sending RPC commands to the running jukebox app. This uses the same interface as the WebUI. Can be used for additional control or for debugging. Use `./run_rpc_tool.sh` to start the tool in interactive mode.

The tool features auto-completion and command history.

The list of available commands is fetched from the running Jukebox service.

The tool can also be used to send commands directly, when passing a `-c` argument, e.g. `./run_rpc_tool.sh -c host.shutdown`.

### Publicity Sniffer

**Scriptname:** [run_publicity_sniffer.sh](../../tools/run_publicity_sniffer.sh)

A command line tool that monitors all messages being sent out from the Jukebox via the publishing interface. Received messages are printed in the console. Mainly used for debugging.
