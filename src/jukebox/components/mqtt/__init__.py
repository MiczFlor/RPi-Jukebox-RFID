import json
import logging
import threading
from typing import Any

import paho.mqtt.client as paho_mqtt

import jukebox.cfghandler
import jukebox.plugs as plugs
import jukebox.publishing
import jukebox.publishing.server
import jukebox.publishing.subscriber

from .mqtt_command_alias import legacy_mqtt_cmd, mqtt_cmd
from .mqtt_const import Mqtt_Attributes, topics_to_send
from .utils import (
    get_args,
    get_current_time_milli,
    get_kwargs,
    get_rpc_command,
    map_repeat_mode,
    split_topic,
)

logger = logging.getLogger("jb.mqtt")
cfg = jukebox.cfghandler.get_handler("jukebox")

base_topic = cfg.setndefault("mqtt", "base_topic", value="phoniebox-dev")
mqtt_enabled = cfg.setndefault('mqtt', 'enable', value=False) is True
legacy_support_enabled = cfg.setndefault("mqtt", "enable_legacy", value=True)


class MQTT(threading.Thread):
    """A thread for monitoring events and publishing interesting events via MQTT."""

    _topic_name: str
    _mqtt_client: paho_mqtt.Client
    _attributes: dict = {}
    _available_cmds = mqtt_cmd

    def __init__(self, client: paho_mqtt.Client):
        super().__init__(name="MqttClient")
        if mqtt_enabled:
            self._mqtt_client = client
            if legacy_support_enabled:
                logger.info("Supporting legacy MQTT commands.")
                self._available_cmds = {**mqtt_cmd, **legacy_mqtt_cmd}

            self.daemon = True
            self._keep_running = True
            self.listen_done = threading.Event()
            self.action_done = threading.Event()
        else:
            logger.info("MQTT Client is disabled")

    def _subscribe(self):
        logger.debug("Subscribing to MQTT topics.")
        self._mqtt_client.message_callback_add(f'{base_topic}/cmd/#', self._on_cmd)

    def _on_cmd(self, client, userdata, msg):
        cmd = split_topic(topic=msg.topic)
        payload = msg.payload.decode("utf-8")
        logger.debug(f'Received MQTT command "{cmd}" with payload "{payload}"')
        try:
            config = self._available_cmds.get(cmd)
            if not config:
                logger.warning(f'No configuration found for MQTT command "{cmd}"')
                return

            rpc = get_rpc_command(config)
            args = get_args(config, payload)
            kwargs = get_kwargs(config, payload)

            if rpc is None:
                logger.warning(f'No RPC call configured for MQTT command "{cmd}"')
                return

            package = rpc.get("package")
            plugin = rpc.get("plugin")
            method = rpc.get("method")

            if package is None:
                raise ValueError(
                    f'Missing "package" attribute for MQTT command "{cmd}"'
                )
            elif plugin is None:
                raise ValueError(f'Missing "plugin" attribute for MQTT command "{cmd}"')
            elif method is None:
                raise ValueError(f'Missing "method" attribute for MQTT command "{cmd}"')
            else:
                logger.info(
                    f'Executing MQTT command "{cmd}" with package="{package}",'
                    + f'plugin="{plugin}", method="{method}", args={args}, kwargs={kwargs}'
                )
                plugs.call_ignore_errors(
                    package=package,
                    plugin=plugin,
                    method=method,
                    args=args,
                    kwargs=kwargs,
                )
        except Exception as e:
            logger.error(
                f"Ignoring failed call for MQTT command '{cmd}': {e}", exc_info=True
            )

    def _publish(self, topic: str, payload: Any, *, qos=0, retain=False):
        """Publish a message via MQTT."""
        logger.debug(
            f'Publishing to topic "{topic}" with payload "{payload}", qos={qos}, retain={retain}'
        )
        self._mqtt_client.publish(
            topic=f"{base_topic}/{topic}",
            payload=json.dumps(payload),
            qos=qos,
            retain=retain,
        )

    def _send_throttled(
        self, topic: str, payload: Any, *, min_time_skip=500, qos=0, retain=False
    ):
        """Send an MQTT message throttled unless value has changed."""
        now = get_current_time_milli()

        if topic in self._attributes:
            prev = self._attributes[topic]
            time_since_last_update = now - prev["last_update"]
            if prev["value"] == payload and time_since_last_update < 30000:
                return
            if prev["value"] != payload and time_since_last_update < min_time_skip:
                return

        logger.debug(
            f'Sending throttled message for topic "{topic}" with payload "{payload}"'
        )
        self._attributes[topic] = {"value": payload, "last_update": now}
        self._publish(topic, payload, retain=retain, qos=qos)

    def _send_player_state(self, payload: Any):
        """Map player state data."""
        self._send_throttled(Mqtt_Attributes.STATE.value, payload["state"])
        for attr in ["title", "artist", "elapsed", "duration", "track", "file"]:
            if attr in payload:
                self._send_throttled(Mqtt_Attributes[attr.upper()].value, payload[attr])

        self._send_throttled(Mqtt_Attributes.RANDOM.value, payload.get("random") == "1")

        repeat_active = bool(payload.get("repeat") == "1")
        self._send_throttled(Mqtt_Attributes.REPEAT.value, repeat_active)
        self._send_throttled(
            Mqtt_Attributes.REPEAT_MODE.value,
            map_repeat_mode(repeat_active, payload.get("single") == "1"),
        )

    def _send_volume(self, payload: Any):
        """Map volume data."""
        logger.debug(f"Sending volume update with payload: {payload}")
        if legacy_support_enabled:
            self._send_throttled(Mqtt_Attributes.VOLUME.value, payload.get("volume"))
            self._send_throttled(Mqtt_Attributes.MUTE.value, bool(payload.get("mute")))
        self._send_throttled("status/player/volume", payload.get("volume"))
        self._send_throttled("status/player/mute", bool(payload.get("mute")))

    def run(self) -> None:
        """Main loop of the MQTT thread."""
        logger.info("Starting MQTT Thread")
        self._send_throttled("state", "online", qos=1, retain=True)
        self._send_throttled("version", jukebox.version(), qos=1, retain=True)  # type: ignore
        self._subscribe()

        sub = jukebox.publishing.subscriber.Subscriber(
            "inproc://PublisherToProxy", topics_to_send
        )
        while self._keep_running:
            topic, payload = sub.receive()
            if topic == "volume.level":
                self._send_volume(payload)
            elif topic == "playerstatus":
                self._send_player_state(payload)
        logger.info("Exiting MQTT Thread")

    def stop(self):
        """Stop the MQTT thread."""
        logger.info("Stopping MQTT Thread")
        self._send_throttled("state", "offline", qos=1, retain=True)

        self._keep_running = False
        self.listen_done.clear()
        self.action_done.set()


mqtt: MQTT
mqtt_client: paho_mqtt.Client


def on_connect(client, userdata, flags, rc):
    """Start thread on successful MQTT connection."""
    global mqtt
    logger.debug(f"Connected with result code {rc} to {base_topic}")
    mqtt = MQTT(client)
    mqtt.start()


@plugs.initialize
def initialize():
    """Setup connection and trigger the MQTT loop."""
    global mqtt_client

    if mqtt_enabled:
        client_id = cfg.setndefault("mqtt", "client_id", value="phoniebox-future3")
        username = cfg.setndefault("mqtt", "username", value="phoniebox-dev")
        password = cfg.setndefault("mqtt", "password", value="phoniebox-dev")
        host = cfg.setndefault("mqtt", "host", value="127.0.0.1")
        port = cfg.setndefault("mqtt", "port", value=1883)

        logger.info(
            f"Initializing MQTT client with client_id={client_id}, username={username}, host={host}, port={port}"
        )
        mqtt_client = paho_mqtt.Client(client_id=client_id)
        mqtt_client.username_pw_set(username=username, password=password)
        mqtt_client.on_connect = on_connect
        mqtt_client.will_set(
            topic=f"{base_topic}/state", payload=json.dumps("offline"), qos=1, retain=True
        )
        mqtt_client.connect(host, port, 60)
        mqtt_client.loop_start()
        logger.info("MQTT client initialized and loop started")
    else:
        logger.info("MQTT client is disabled")


@plugs.atexit
def atexit(signal_id: int, **ignored_kwargs):
    global mqtt, mqtt_client
    if mqtt_enabled:
        logger.info("Executing atexit handler, stopping MQTT client")
        mqtt.stop()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logger.info("MQTT client stopped and disconnected")
    else:
        logger.info("MQTT client is disabled")
