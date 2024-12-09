# MQTT Integration

The MQTT integration allows you to control your Phoniebox via the MQTT protocol. This feature enables not only MQTT
control but also integration with home automation systems like Home Assistant.

## Configuration

Set the corresponding setting in `shared\settings\jukebox.yaml` to activate this feature.

``` yaml
modules:
    named:
        ...
        mqtt: mqtt
...
mqtt:
    enable: true
    # The prefix for the mqtt topic. /{base_topic}/{topic}
    base_topic: phoniebox-dev
    # Enable support for legacy commands. Only needed for compatiblity to previous phoniebox mqtt integration.
    enable_legacy: false
    # The client id used in communication with the MQTT broker and identification of the phoniebox
    client_id: phoniebox_dev
    # The username to authenticate against the broker
    username: phoniebox-dev
    # The password to authenticate against the broker
    password: phoniebox-dev
    # The host name or IP address of your mqtt broker
    host: 127.0.0.1
    # The port number of the mqtt broker. The default is 1883
    port: 1883
```

## Usage in Home Assistant

Home Assistant does not have a native MQTT Media Player integration. To integrate Phoniebox into Home Assistant, you
can use the Universal Media Player configuration in combination with the Home Assistant MQTT service.

There is also an HACS addon adding Phoniebox as Media Player [Hass Phoniebox](https://github.com/c0un7-z3r0/hass-phoniebox).
