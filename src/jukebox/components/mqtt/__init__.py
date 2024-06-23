"""MQTT Plugin Package."""

import json
import logging
import threading
import time
from typing import Any

import paho.mqtt.client as paho_mqtt
from components.rpc_command_alias import cmd_alias_definitions

import jukebox.cfghandler
import jukebox.plugs as plugs
import jukebox.publishing
import jukebox.publishing.server
import jukebox.publishing.subscriber

from .mqtt_command_alias import legacy_mqtt_cmd, mqtt_cmd
from .mqtt_const import Mqtt_Attributes, topics_to_send

logger = logging.getLogger("jb.mqtt")
cfg = jukebox.cfghandler.get_handler("jukebox")

base_topic = cfg.setndefault("mqtt", "base_topic", value="phoniebox-dev")
legacy_support_enabled = cfg.setndefault("mqtt", "enable_legacy", value=True)

REPEAT_MODE_OFF = "off"
REPEAT_MODE_SINGLE = "single"
REPEAT_MODE_PLAYLIST = "playlist"


def _get_current_time_milli():
    return int(round(time.time() * float(1000)))


def _split_topic(topic: str):
    parts = topic.split("/")
    return parts[2] if len(parts) == 3 else parts[1]


def _map_repeat_mode(repeat_active: bool, single_active: bool):
    """Try to find the correct repeat mode."""
    if repeat_active is False:
        return REPEAT_MODE_OFF
    if single_active is True:
        return REPEAT_MODE_SINGLE
    return REPEAT_MODE_PLAYLIST


def _get_args(config: Any, payload: str):
    if "args" not in config:
        return None
    elif hasattr(config["args"], "__call__"):
        return config["args"](payload)
    return config["args"]


def _get_rpc_command(config: Any):
    if "rpc" not in config:
        return None
    elif isinstance(config["rpc"], str):
        return cmd_alias_definitions[config["rpc"]]
    return config["rpc"]


def _get_kwargs(config: Any, payload: dict[str, Any]):
    if "kwargs" not in config:
        return None
    elif hasattr(config["kwargs"], "__call__"):
        return config["kwargs"](payload)
    return config["kwargs"]


class MQTT(threading.Thread):
    global mqtt_client
    """A thread for monitoring the events and publish intersting events via mqtt."""
    _topic_name: str
    _mqtt_client: paho_mqtt.Client
    _attributes = dict()
    _available_cmds = mqtt_cmd

    def __init__(self, client: paho_mqtt.Client):
        super().__init__(name="MqttClient")
        self._mqtt_client = client
        if legacy_support_enabled is True:
            logger.info("Supporting legacy mqtt commands.")
            self._available_cmds = {**mqtt_cmd, **legacy_mqtt_cmd}

        self.daemon = True
        self._keep_running = True
        self.listen_done = threading.Event()
        self.action_done = threading.Event()

    def _subscribe(self):
        self._mqtt_client.message_callback_add("phoniebox-dev/cmd/#", self._on_cmd)

    def _on_cmd(self, client, userdata, msg):
        cmd = _split_topic(topic=msg.topic)
        payload = msg.payload.decode("utf-8")
        logger.debug(f'Received MQTT cmd "{cmd}" {payload}')
        try:
            config = self._available_cmds[cmd]
            rpc = _get_rpc_command(config)
            args = _get_args(config, payload)
            kwargs = _get_kwargs(config, payload)

            if rpc is None:
                logger.warn(f'No rpc call configured for MQTT command "{cmd}"')
                return

            plugs.call_ignore_errors(
                package=rpc["package"],
                plugin=rpc["plugin"],
                method=rpc["method"] if "method" in rpc else None,
                args=args,
                kwargs=kwargs,
            )
        except Exception as e:
            logger.error(f"Ignoring failed call: ({cmd})  {e}")

    def _publish(self, topic: str, payload: Any, *, qos=0, retain=False):
        """Publish the message via mqtt."""
        self._mqtt_client.publish(
            topic=f"{base_topic}/{topic}",
            payload=json.dumps(payload),
            qos=qos,
            retain=retain,
        )

    def _send_throttled(
        self, topic, payload, *, min_time_skip=500, qos=0, retain=False
    ):
        """Send mqtt message throttled unless value changed."""
        now = _get_current_time_milli()

        if topic in self._attributes:
            prev = self._attributes[topic]
            time_since_last_update = now - prev["last_update"]
            if prev["value"] == payload and time_since_last_update < 30000:
                return
            if prev["value"] != payload and time_since_last_update < min_time_skip:
                return

        self._attributes[topic] = {"value": payload, "last_update": now}
        self._publish(topic, payload, retain=retain, qos=qos)

    def _send_player_state(self, payload: Any):
        """Map the player state data."""
        self._send_throttled(Mqtt_Attributes.STATE.value, payload["state"])
        if "title" in payload:
            self._send_throttled(Mqtt_Attributes.TITLE.value, payload["title"])
        if "artist" in payload:
            self._send_throttled(Mqtt_Attributes.ARTIST.value, payload["artist"])
        if "elapsed" in payload:
            self._send_throttled(
                Mqtt_Attributes.ELAPSED.value,
                payload["elapsed"],
                min_time_skip=2000,
            )
        if "duration" in payload:
            self._send_throttled(Mqtt_Attributes.DURATION.value, payload["duration"])
        if "track" in payload:
            self._send_throttled(Mqtt_Attributes.TRACK.value, payload["song"])
        if "file" in payload:
            self._send_throttled(Mqtt_Attributes.FILE.value, payload["file"])

        self._send_throttled(Mqtt_Attributes.RANDOM.value, payload["random"] == "1")

        repeat_active = bool(payload["repeat"] == "1")
        self._send_throttled(Mqtt_Attributes.REPEAT.value, repeat_active)
        self._send_throttled(
            Mqtt_Attributes.REPEAT_MODE.value,
            _map_repeat_mode(repeat_active, payload["single"] == "1"),
        )

    def _send_volume(self, payload: Any):
        """Map the volume data."""
        if legacy_support_enabled:
            self._send_throttled(Mqtt_Attributes.VOLUME.value, payload["volume"])
            self._send_throttled(Mqtt_Attributes.MUTE.value, bool(payload["mute"]))
        self._send_throttled("status/player/volume", payload["volume"])
        self._send_throttled("status/player/mute", bool(payload["mute"]))

    def run(self) -> None:
        """The main loop of the MQTT thread."""
        logger.info("Start MQTT Thread")
        self._send_throttled("state", "online", qos=1, retain=True)
        self._subscribe()

        sub = jukebox.publishing.subscriber.Subscriber(
            "inproc://PublisherToProxy", topics_to_send
        )
        while self._keep_running:
            [topic, payload] = sub.receive()
            if topic == "volume.level":
                self._send_volume(payload)
            elif topic == "playerstatus":
                self._send_player_state(payload)
        logger.info("Exit MQTT Thread")

    def stop(self):
        """Stop the mqtt thread"""
        logger.info("Stopping MQTT Thread")
        self._send_throttled("state", "offline", qos=1, retain=True)

        self._keep_running = False
        self.listen_done.clear()
        self.action_done.set()


mqtt: MQTT
mqtt_client: paho_mqtt.Client


def on_connect(client, userdata, flags, rc):
    """Start thread on successful mqtt connection."""

    global mqtt
    logger.debug(f"Connected with result code {rc} {base_topic}")

    mqtt = MQTT(client)
    mqtt.start()


@plugs.initialize
def initialize():
    """Setup connection and trigger the mqtt loop."""

    global mqtt_client

    client_id = cfg.setndefault("mqtt", "base_topic", value="phoniebox-future3")
    username = cfg.setndefault("mqtt", "username", value="phoniebox-dev")
    password = cfg.setndefault("mqtt", "password", value="phoniebox-dev")
    host = cfg.setndefault("mqtt", "host", value="127.0.0.1")
    port = cfg.setndefault("mqtt", "port", value=1883)

    mqtt_client = paho_mqtt.Client(client_id=client_id)
    mqtt_client.username_pw_set(username=username, password=password)
    mqtt_client.on_connect = on_connect
    mqtt_client.will_set(
        topic=f"{base_topic}/state", payload=json.dumps("offline"), qos=1, retain=True
    )
    mqtt_client.connect(host, port, 60)
    mqtt_client.loop_start()


@plugs.atexit
def atexit(signal_id: int, **ignored_kwargs):
    global mqtt, mqtt_client
    mqtt.stop()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
