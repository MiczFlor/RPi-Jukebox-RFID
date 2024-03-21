# Event devices

## Background

Event devices are generic input devices that are exposed in `/dev/input`.
This includes USB peripherals (Keyboards, Controllers, Joysticks or Mouse) as well as potentially bluetooth devices.

A specific usecase for this could be, if a Zero Delay Arcade USB Encoder is used to wire arcade buttons instead of using GPIO pins.

These device interface support various kinds of input events, such as press, movements and potentially also outputs (eg. rumble, led lights, ...). Currently only the usage of button presses as input is supported.

This functionality was previously implemented under the name of [USB buttons](https://github.com/MiczFlor/RPi-Jukebox-RFID/blob/develop/components/controls/buttons_usb_encoder/README.md).

The devices and their button mappings need to be mapped in the configuration file.

## Configuration

To configure event devices, first add the plugin as an entry to the module list of your main configuration file ``shared/settings/jukebox.yaml``:

``` yaml
modules:
  named:
    event_devices: controls.event_devices
```

And add the following section with the plugin specific configuration:

``` yaml
evdev:
  enabled: true
  config_file: ../../shared/settings/evdev.yaml
```

The actual configuration itself is stored in a separate file. In this case in ``../../shared/settings/evdev.yaml``.

The configuration is structured akin to the configuration of the [GPIO devices](./gpio.md).

In contrast to `gpio`, multiple devices (eg arcade controllser, keyboards, joysticks, mice, ...) are supported, each with their own `input_devices` (=buttons). `output_devices` or actions other than `on_press` are currently not yet supported.

``` yaml
devices: # list of devices to listen for
  {device nickname}: # config for a specific device
    device_name: {device_name} # name of the device
    exact: False/True # optional to require exact match. Otherwise it is sufficient that a part of the name matches
    input_devices: # list of buttons to listen for for this device
      {button nickname}:
        type: Button
        kwargs:
          key_code: {key-code}: # evdev event id
        actions:
          on_press: # Currently only the on_press action is supported
            {rpc_command_definition} # eg `alias: toggle`
```

The `{device nickname}` is only for your own orientation and can be choosen freely.
For each device you need to figure out the `{device_name}` and the `{event_id}` corresponding to key strokes, as indicated in the sections below.

### Identifying the `{device_name}`

The `{device_name}` can be identified using the following Python snippet:

``` Python
import evdev
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)
```

The output could be in the style of:

```text
/dev/input/event1    Dell Dell USB Keyboard   usb-0000:00:12.1-2/input0
/dev/input/event0    Dell USB Optical Mouse   usb-0000:00:12.0-2/input0
```

In this example, the `{device_name}` could be `DELL USB Optical Mouse`.
Note that if you use the option `exact: False`, it would be sufficient to add a substring such as `USB Keyboard`.

### Identifying the `{key-code}`

The key code for a button press can be determined using the following code snippet:

``` Python
import evdev
device = evdev.InputDevice('/dev/input/event0')
device.capabilities(verbose=True)[('EV_KEY', evdev.ecodes.EV_KEY)]
```

With the `InputDevice` corresponding to the path from the output of the section `{device_name}` (eg. in the example `/dev/input/event0`
would correspond to `Dell Dell USB Keyboard`).

If the naming is not clear, it is also possible to empirically check for the key code by listening for events:

``` Python
from evdev import InputDevice, categorize, ecodes
dev = InputDevice('/dev/input/event1')
print(dev)
for event in dev.read_loop():
  if event.type == ecodes.EV_KEY:
    print(categorize(event))
```

The output could be of the form:

```text
device /dev/input/event1, name "DragonRise Inc.   Generic   USB  Joystick  ", phys "usb-3f980000.usb-1.2/input0"
key event at 1672569673.124168, 297 (BTN_BASE4), down
key event at 1672569673.385170, 297 (BTN_BASE4), up
```

In this example output, the `{key-code}` would be `297`

Alternatively, the device could also be setup without a mapping.
Afterwards, when pressing keys, the key codes can be found in the log files. Press various buttons on your device,
while watching the logs with `tail -f shared/logs/app.log`.
Look for entries like `No callback registered for button ...`.

### Specifying the `{rpc_command_definition}`

The RPC command follows the regular RPC command rules as defined in the [following documentation](./rpc-commands.md).

## Full example config

A complete configuration example for a USB Joystick controller can be found in the [examples](../../resources/default-settings/evdev.example.yaml).
