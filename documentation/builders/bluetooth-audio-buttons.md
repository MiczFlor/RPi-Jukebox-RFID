# Bluetooth

## Bluetooth Audio Buttons

When a bluetooth sound device (headphone, speakers) connects attempt to
automatically listen to it's buttons (play, next, etc.)

The bluetooth input device name is matched automatically from the
bluetooth sound card device name. During boot up, it is uncertain if the
bluetooth device connects first, or the Jukebox service is ready first.
Therefore, after service initialization, already connected bluetooth
sound devices are scanned and an attempt is made to find their input
buttons.

> [!NOTE]
> If the automatic matching fails, there currently is no manual configuration option. Open an issue ticket if you have problems with the automatic matching.

Button key codes are standardized and by default the buttons play,
pause, next song, previous song are recognized. Volume up/down is
handled independently from this module by PulseAudio and the bluetooth
audio transmission protocol.

The module needs to be enabled in the main configuration file with:

``` yaml
bluetooth_audio_buttons:
  enable: true
```

### Custom key bindings

You may change or extend the actions assigned to a button in the
configuration. If the configuration contains a block 'mapping', the
default button-action mapping is *completely* replaced with the new
mapping. The definitions for each key looks like
`key-code: {rpc_command_definition}`. The RPC command follows the
regular RPC command rules as defined in
[RPC Commands](rpc-commands.md).

``` yaml
bluetooth_audio_buttons:
  enable: true
  mapping:
    # Play & pause both map to toggle which is also the usual behaviour of headsets
    200:
      alias: toggle
    201:
      alias: toggle
    # Re-map next song button, to set defined output volume (for some fun)
    163:
      package: volume
      plugin: ctrl
      method: set_volume
      args: [18]
    # Re-map prev song button to shutdown
    165:
      alias: shutdown
```

Key codes can be found in the log files. Press the various buttons on
your headset, while watching the logs with e.g.
`tail -f shared/logs/app.log`. Look for entries like
`No callback registered for button ...`.
