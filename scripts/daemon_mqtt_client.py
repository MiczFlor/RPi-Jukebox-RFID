#!/usr/bin/python3
import paho.mqtt.client as mqtt
import os.path, subprocess, re, ssl, time, datetime


# ----------------------------------------------------------
#  Prerequisites
# ----------------------------------------------------------
# pip3 install paho-mqtt


# ----------------------------------------------------------
#  SETTINGS
# ----------------------------------------------------------
DEBUG=False
mqttBaseTopic="phoniebox"				# MQTT base topic
mqttClientId="phoniebox"				# MQTT client ID
mqttHostname="openHAB"					# MQTT server hostname
mqttPort=8883							# MQTT server port (typically 1883 for unencrypted, 8883 for encrypted)
mqttUsername=""							# username for user/pass based authentication
mqttPassword=""							# password for user/pass based authentication
mqttCA="mqtt-ca.crt"					# path to server certificate for certificate-based authentication
mqttCert="mqtt-client-phoniebox.crt"	# path to client certificate for certificate-based authentication
mqttKey="mqtt-client-phoniebox.key"		# path to client keyfile for certificate-based authentication
mqttConnectionTimeout=60				# in seconds; timeout for MQTT connection
refreshInterval=30						# in seconds; how often should the status be sent to MQTT



# ----------------------------------------------------------
#  DO NOT CHANGE BELOW
# ----------------------------------------------------------

# absolute script path
path = os.path.dirname(os.path.realpath(__file__))

# list of available commands and attributes
arAvailableCommands = ['volumeup', 'volumedown', 'mute', 'playerpause', 'playernext', 'playerprev']
arAvailableAttributes = ['volume', 'mute', 'repeat', 'random', 'state', 'file', 'artist', 'albumartist' , 'title', 'album', 'track', 'elapsed', 'duration', 'trackdate', 'last_card']

def on_connect(client, userdata, flags, rc):
	if rc==0:
		print("Connection established.")
		
		# retrieve server version and edition
		with open(path + "/../settings/version", "r") as f:
			version = f.read()
		
		with open(path + "/../settings/edition", "r") as f:
			edition = f.read()
		
		# publish general server info
		client.publish(mqttBaseTopic + "/state", payload="online", qos=1, retain=True)
		client.publish(mqttBaseTopic + "/version", payload=version, qos=1, retain=True)
		client.publish(mqttBaseTopic + "/edition", payload=edition, qos=1, retain=True)
		
	else:
		print("Connection could NOT be established. Return-Code:", rc)


def on_disconnect(client, userdata, rc):
	print("Disconnecting. Return-Code:", str(rc))
	client.loop_stop()


def on_log(client, userdata, level, buf):
	print("   [LOG]", buf)


def on_message(client, userdata, message):
	print("")
	print("MQTT message incoming to subscriptions...")
	print(" - topic =", message.topic)
	print(" - value =", message.payload.decode("utf-8"))

	if message.topic == mqttBaseTopic + "/set":
		processSet(message)

	elif message.topic == mqttBaseTopic + "/get":
		processGet(message)
	

def processSet(message):
	command = message.payload.decode("utf-8")
	if command == "help":
		availableCommands = ", ".join(arAvailableCommands)
		client.publish(mqttBaseTopic + "/available_commands", payload=availableCommands)
		print(" --> Publishing response", availableAttributes)

	elif command in arAvailableCommands:
		check_call(path + "/playout_controls.sh -c=" + command, shell=True)
		print(" --> Sending command " + command + " to MPD")

	else:
		print(" --> Unknown command", command)


def processGet(message):
	attribute = message.payload.decode("utf-8")
	mpd_status = fetchMPDStatus()
	if attribute == "all":
		for attribute in mpd_status:
			client.publish(mqttBaseTopic + "/attribute/" + attribute, payload=mpd_status[attribute])
			print(" --> Publishing response " + attribute + " = " + mpd_status[attribute])

	elif attribute in mpd_status:
		client.publish(mqttBaseTopic + "/attribute/" + attribute, payload=mpd_status[attribute])
		print(" --> Publishing response " + attribute + " = " + mpd_status[attribute])
	
	elif attribute == "last_card":
		# retrieve last card ID
		with open(path + "/../settings/Latest_RFID", "r") as f:
			last_card = f.read()
		client.publish(mqttBaseTopic + "/attribute/last_card", payload=last_card)
		print(" --> Publishing response " + attribute + " = " + last_card)

	elif attribute == "help":
		availableAttributes = ", ".join(arAvailableAttributes)
		client.publish(mqttBaseTopic + "/available_attributes", payload=availableAttributes)
		print(" --> Publishing response", availableAttributes)
	
	else:
		print(" --> Could not retrieve attribute", attribute)


def fetchMPDStatus():
	result = {}

	# fetch status from MPD
	cmd = ['nc', '-w', '1', 'localhost', '6600']
	input = 'status\ncurrentsong\nclose'.encode('utf-8')
	status = subprocess.run(cmd, stdout=subprocess.PIPE, input=input).stdout.decode('utf-8')

	# interpret status
	result["volume"] = re.search('\nvolume: (.*)\n', status).group(1)
	result["repeat"] = re.search('\nrepeat: (.*)\n', status).group(1)
	result["random"] = re.search('\nrandom: (.*)\n', status).group(1)
	result["state"] = re.search('\nstate: (.*)\n', status).group(1)

	# interpret mute state based on volume
	if result["volume"] == '0':
		result["mute"] = "true"
	else:
		result["mute"] = "false"

	# interpret metadata when in play/pause mode
	if result["state"] != "stop":
		result["file"] = re.search('\nfile: (.*)\n', status).group(1)
		result["artist"] = re.search('\nArtist: (.*)\n', status).group(1)
		result["albumartist"] = re.search('\nAlbumArtist: (.*)\n', status).group(1)
		result["title"] = re.search('\nTitle: (.*)\n', status).group(1)
		result["album"] = re.search('\nAlbum: (.*)\n', status).group(1)
		result["track"] = re.search('\nTrack: (.*)\n', status).group(1)
		result["trackdate"] = re.search('\nDate: (.*)\n', status).group(1)

		elapsed = int(float(re.search('\nelapsed: (.*)\n', status).group(1)))
		hours, remainder = divmod(elapsed, 3600)
		minutes, seconds = divmod(remainder, 60)
		result["elapsed"] = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

		duration = int(float(re.search('\nduration: (.*)\n', status).group(1)))
		hours, remainder = divmod(duration, 3600)
		minutes, seconds = divmod(remainder, 60)
		result["duration"] = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

	return result




# create client instance
client = mqtt.Client(mqttClientId)

# configure authentication
if mqttUsername != "" and mqttPassword != "":
	client.username_pw_set(username=mqttUsername, password=mqttPassword)

if mqttCert != "" and mqttKey != "":
	if mqttCA != "":
		client.tls_set(ca_certs=mqttCA, certfile=mqttCert, keyfile=mqttKey)
	else:
		client.tls_set(certfile=mqttCert, keyfile=mqttKey)
elif mqttCA != "":
	client.tls_set(ca_certs=mqttCA)

# attach event handlers
client.on_connect=on_connect
client.on_disconnect=on_disconnect
client.on_message=on_message
if DEBUG == True:
	client.on_log=on_log

# define last will
client.will_set(mqttBaseTopic + "/state", payload="offline", qos=1, retain=True)

# connect to MQTT server
print("Connecting to " + mqttHostname + " on port " + str(mqttPort))
client.connect(mqttHostname, mqttPort, mqttConnectionTimeout)

# subscribe to topics
client.subscribe(mqttBaseTopic + "/get")
client.subscribe(mqttBaseTopic + "/set")

# start endless loop
client.loop_start()
while True:
	client.publish(mqttBaseTopic + "/get", payload="all")
	time.sleep(refreshInterval)
