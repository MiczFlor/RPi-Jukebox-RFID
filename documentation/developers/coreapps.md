# Jukebox Apps

The Jukebox's core apps are located in `src/jukebox`. To learn more about each app and its parameters, run the following command:

``` bash
$ cd src/jukebox
$ ./<scriptname> -h
```

## Jukebox Core

**Scriptname:** [run_jukebox.sh](../../run_jukebox.sh)

This is the main app. It starts the Jukebox Core.

This runs as a service, which starts automatically after boot-up. At times, it may be necessary to restart the service, for example, after a configuration change. Not all configuration changes can be applied on-the-fly. See [Jukebox Configuration](../builders/configuration.md#jukebox-configuration).

For debugging, it's best to run Jukebox directly from the console rather than as a service, as this provides direct logging information in the console and allows for changing command line parameters. See [Troubleshooting](../builders/troubleshooting.md).

## Configuration Tools

Before running the configuration tools, stop the Jukebox Core service.
See [Best practice procedure](../builders/configuration.md#best-practice-procedure).

### Audio

**Scriptname:** [setup_configure_audio.sh](../../installation/components/setup_configure_audio.sh)

A setup tool to register the PulseAudio sinks as primary and secondary audio outputs.

This will also set up an equalizer and mono downmixer in the PulseAudio configuration file. Run this once after installation. It can be re-run at any time to change the settings. For more information see [Audio Configuration](../builders/audio.md).

### RFID Reader

**Scriptname:** [setup_rfid_reader.sh](../../installation/components/setup_rfid_reader.sh)

Setup tool to configure the RFID Readers.

Run this once to register and configure the RFID readers with Jukebox. It can be re-run at any time to change the settings. For more information see [RFID Readers](./rfid/README.md).

> [!NOTE]
> This tool will always create a new configuration file, thereby overwriting the old one (after confirming with the user). Any manual modifications to the settings will need to be reapplied.

## Developer Tools

### RPC

**Scriptname:** [run_rpc_tool.sh](../../tools/run_rpc_tool.sh)

Command Line Interface to the Jukebox RPC Server.

A command-line tool for sending RPC commands to the running Jukebox app, utilizing the same interface as the Web App, provides additional control or debugging capabilities. Start the tool in interactive mode with `./run_rpc_tool.sh`.

Features include auto-completion and command history, with available commands fetched from the running Jukebox service.

For direct command execution, use the `-c` argument, e.g., `./run_rpc_tool.sh -c host.shutdown`.

### Publicity Sniffer

**Scriptname:** [run_publicity_sniffer.sh](../../tools/run_publicity_sniffer.sh)

This command-line tool monitors all messages sent from Jukebox through the publishing interface, printing received messages in the console. It is primarily used for debugging.
