"""MQTT Plugin Package."""

import json
import logging
import time
from typing import Any
import jukebox.cfghandler
import jukebox.plugs as plugs
import jukebox.publishing
import jukebox.publishing.server
import jukebox.publishing.subscriber
import threading
import paho.mqtt.client as paho_mqtt


logger = logging.getLogger('jb.mqtt')
cfg = jukebox.cfghandler.get_handler('jukebox')

base_topic = cfg.setndefault('mqtt', 'base_topic', value="phoniebox-dev")
topics_to_send = ["volume.level", "playerstatus"]

REPEAT_MODE_OFF = "off"
REPEAT_MODE_SINGLE = "single"
REPEAT_MODE_PLAYLIST = "playlist"


def _get_current_time_milli():
    return int(round(time.time() * 1000))


class MQTT(threading.Thread):
    """A thread for monitoring the events and publish intersting events via mqtt."""
    _topic_name: str
    _mqtt_client: paho_mqtt
    _attributes = dict()

    def __init__(self, client: paho_mqtt.Client):
        super().__init__(name='MqttClient')
        self._mqtt_client = client
        self._send_throttled("state", "online")

        self.daemon = True
        self._keep_running = True
        self.listen_done = threading.Event()
        self.action_done = threading.Event()

    def _publish_attr(self, topic: str, payload: Any):
        """Publish the attribute via mqtt."""
        self._publish(f"attribute/{topic}", payload)

    def _publish(self, topic: str, payload: Any):
        """Publish the message via mqtt."""
        self._mqtt_client.publish(f"{base_topic}/{topic}", json.dumps(payload))

    def _send_throttled(self, topic, payload):
        """Send mqtt message throttled unless value changed."""
        now = _get_current_time_milli()

        if topic in self._attributes:
            prev = self._attributes[topic]
            time_since_last_update = now - prev['last_update']
            if prev['value'] == payload and time_since_last_update < 30000:
                return
            if prev['value'] != payload and time_since_last_update < 1000:
                return

        self._attributes[topic] = {
            'value': payload,
            'last_update': now
        }
        self._publish_attr(topic, payload)

    def _send_player_state(self, payload: Any):
        """Map the player state data."""
        self._send_throttled("state", payload["state"])
        if "title" in payload:
            self._send_throttled("title", payload["title"])
        if "artist" in payload:
            self._send_throttled("artist", payload["artist"])
        if "elapsed" in payload:
            self._send_throttled("elapsed", payload["elapsed"])
        if "duration" in payload:
            self._send_throttled("duration", payload["duration"])
        if "track" in payload:
            self._send_throttled("track", payload["song"])
        if "file" in payload:
            self._send_throttled("file", payload["file"])
        self._send_throttled("random", payload["random"] == "1")
        repeat_active = bool(payload["repeat"] == "1")
        self._send_throttled("repeat", repeat_active)
        self._send_throttled("repeat_mode", self._map_repeat_mode(repeat_active, payload["single"] == "1"))

    def _send_volume(self, payload: Any):
        """Map the volume data."""
        self._send_throttled("volume", payload["volume"])
        self._send_throttled("mute", bool(payload["mute"]))

    def _map_repeat_mode(self, repeat_active: bool, single_active: bool):
        """Try to find the correct repeat mode."""
        if repeat_active is False:
            return REPEAT_MODE_OFF
        if single_active is True:
            return REPEAT_MODE_SINGLE
        return REPEAT_MODE_PLAYLIST

    def run(self) -> None:
        """The main loop of the MQTT thread."""
        logger.info('Start MQTT Thread')
        sub = jukebox.publishing.subscriber.Subscriber("inproc://PublisherToProxy", topics_to_send)
        while self._keep_running:
            [topic, payload] = sub.receive()
            logger.debug(f"{topic}: {payload}")
            if topic == "volume.level":
                self._send_volume(payload)
            elif topic == "playerstatus":
                self._send_player_state(payload)
        logger.info('Exit MQTT Thread')

    def stop(self):
        """Stop the mqtt thread"""
        logger.debug('Stop request received')
        self._publish_attr("state", 'offline')

        self._keep_running = False
        self.listen_done.clear()
        self.action_done.set()


mqtt: MQTT
mqtt_client: paho_mqtt.Client


def on_connect(client, userdata, flags, rc):
    """Start thread on successful mqtt connection."""

    global status_thread, mqtt
    logger.debug(f"Connected with result code {rc} {base_topic}")

    mqtt = MQTT(client)
    mqtt.start()


@plugs.initialize
def initialize():
    """Setup connection and trigger the mqtt loop."""

    global mqtt_client

    client_id = cfg.setndefault('mqtt', 'base_topic', value="phoniebox-future3")
    username = cfg.setndefault('mqtt', 'username', value="phoniebox-dev")
    password = cfg.setndefault('mqtt', 'password', value="phoniebox-dev")
    host = cfg.setndefault('mqtt', 'host', value="127.0.0.1")
    port = cfg.setndefault('mqtt', 'port', value=1883)

    mqtt_client = paho_mqtt.Client(client_id=client_id)
    mqtt_client.username_pw_set(
        username=username, password=password
    )
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(host, port, 60)
    mqtt_client.loop_start()


@plugs.atexit
def atexit(**ignored_kwargs):
    global mqtt, mqtt_client
    mqtt.stop()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
