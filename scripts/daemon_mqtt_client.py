#!/usr/bin/env python3

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
mqttPort=8883						# MQTT server port (typically 1883 for unencrypted, 8883 for encrypted)
mqttUsername=""						# username for user/pass based authentication
mqttPassword=""						# password for user/pass based authentication
mqttCA="/home/pi/MQTT/mqtt-ca.crt"			# path to server certificate for certificate-based authentication
mqttCert="/home/pi/MQTT/mqtt-client-phoniebox.crt"	# path to client certificate for certificate-based authentication
mqttKey="/home/pi/MQTT/mqtt-client-phoniebox.key"	# path to client keyfile for certificate-based authentication
mqttConnectionTimeout=60				# in seconds; timeout for MQTT connection
refreshIntervalPlaying=5				# in seconds; how often should the status be sent to MQTT (while playing)
refreshIntervalIdle=30					# in seconds; how often should the status be sent to MQTT (when NOT playing)


# ----------------------------------------------------------
#  DO NOT CHANGE BELOW
# ----------------------------------------------------------

# absolute script path
path = os.path.dirname(os.path.realpath(__file__))

# internal refresh interval
refreshInterval = refreshIntervalPlaying

# list of available commands and attributes
arAvailableCommands = ['volumeup', 'volumedown', 'mute', 'playerplay', 'playerpause', 'playernext', 'playerprev', 'playerstop', 'playerrewind', 'playershuffle', 'playerreplay', 'scan', 'shutdown', 'shutdownsilent', 'reboot', 'disablewifi']
arAvailableCommandsWithParam = ['setvolume', 'setvolstep', 'setmaxvolume', 'setidletime', 'playerseek', 'shutdownafter', 'playerstopafter', 'playerrepeat', 'rfid', 'gpio']
arAvailableAttributes = ['volume', 'mute', 'repeat', 'random', 'state', 'file', 'artist', 'albumartist' , 'title', 'album', 'track', 'elapsed', 'duration', 'trackdate', 'last_card', 'maxvolume', 'volstep', 'idletime', 'rfid', 'gpio']


def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Connection established.")

		# retrieve server version and edition
		version = readfile(path + "/../settings/version")
		edition = readfile(path + "/../settings/edition")

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

	regex_extract = re.search(mqttBaseTopic + '\/(.*)\/(.*)', message.topic)
	message_topic = regex_extract.group(1).lower()
	message_subtopic = regex_extract.group(2).lower()
	message_payload = message.payload.decode("utf-8")

	if message_topic == "cmd":
		processCmd(message_subtopic, message_payload)

	elif message_topic == "get":
		processGet(message_subtopic)


def processCmd(command, parameter):
	# list all commands
	if command == "help":
		availableCommands = ", ".join(arAvailableCommands)
		availableCommandsWithParam = ", ".join(arAvailableCommandsWithParam)
		client.publish(mqttBaseTopic + "/available_commands", payload=availableCommands)
		client.publish(mqttBaseTopic + "/available_commands_with_params", payload=availableCommandsWithParam)
		print(" --> Publishing response available_commands =", availableCommands)
		print(" --> Publishing response available_commands_with_params =", availableCommandsWithParam)

	# toggle RFID reader daemon
	elif command == "rfid":
		parameter = parameter.lower()
		if parameter == "start" or parameter == "stop":
			subprocess.call(["sudo /bin/systemctl " + parameter + " phoniebox-rfid-reader.service"], shell=True)
			processGet("rfid")
		else:
			print(" --> Expecting parameter start or stop")

	# toggle GPIO button daemon
	elif command == "gpio":
		parameter = parameter.lower()
		if parameter == "start" or parameter == "stop":
			subprocess.call(["sudo /bin/systemctl " + parameter + " phoniebox-gpio-buttons.service"], shell=True)
			processGet("gpio")
		else:
			print(" --> Expecting parameter start or stop")

	# all the other known commands w/o param
	elif command in arAvailableCommands:
		print(" --> Sending command " + command + " to playout_controls.sh")
		subprocess.call([path + "/playout_controls.sh -c=" + command], shell=True)

	# all the other known commands /w param
	elif command in arAvailableCommandsWithParam:
		print(" --> Sending command " + command + " and value " + parameter + " to playout_controls.sh")
		subprocess.call([path + "/playout_controls.sh -c=" + command + " -v=" + parameter], shell=True)

	# we don't know this command
	else:
		print(" --> Unknown command", command)


def processGet(attribute):
	mpd_status = fetchData()

	# respond with all attributes
	if attribute == "all":
		for attribute in mpd_status:
			client.publish(mqttBaseTopic + "/attribute/" + attribute, payload=mpd_status[attribute])
			print(" --> Publishing response " + attribute + " = " + mpd_status[attribute])

	# list all possible attributes
	elif attribute == "help":
		availableAttributes = ", ".join(arAvailableAttributes)
		client.publish(mqttBaseTopic + "/available_attributes", payload=availableAttributes)
		print(" --> Publishing response", availableAttributes)

	# all the other known attributes
	elif attribute in mpd_status:
		client.publish(mqttBaseTopic + "/attribute/" + attribute, payload=mpd_status[attribute])
		print(" --> Publishing response " + attribute + " = " + mpd_status[attribute])

	# we don't know this attribute
	else:
		print(" --> Could not retrieve attribute", attribute)


def readfile(filepath):
	result = ""
	with open(filepath, "r") as f:
		result = f.read()
	return result.rstrip()


def isServiceRunning(svc):
	cmd = ['/bin/systemctl', 'status', svc]
	status = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()
	if re.search('\n.*Active:.*running.*\n', status):
		return "true"
	else:
		return "false"


def normalizeTrueFalse(s):
	if s == "0":
		return "false"
	else:
		return "true"


def fetchData():
	# use global refreshInterval as this function is run as a thread through the paho-mqtt loop
	global refreshInterval

	result = {}

	# fetch status from MPD
	cmd = ['nc', '-w', '1', 'localhost', '6600']
	input = 'status\ncurrentsong\nclose'.encode('utf-8')
	status = subprocess.run(cmd, stdout=subprocess.PIPE, input=input).stdout.decode('utf-8')

	# interpret status
	result["state"] = re.search('\nstate: (.*)\n', status).group(1).lower()
	result["volume"] = re.search('\nvolume: (.*)\n', status).group(1)
	result["repeat"] = normalizeTrueFalse(re.search('\nrepeat: (.*)\n', status).group(1))
	result["random"] = normalizeTrueFalse(re.search('\nrandom: (.*)\n', status).group(1))

	# interpret mute state based on volume
	if result["volume"] == "0":
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

	# fetch some more data from global.conf (via playout_controls.sh)
	result["maxvolume"] = subprocess.run(['../scripts/playout_controls.sh', '-c=getmaxvolume'], stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()
	result["volstep"] = subprocess.run(['../scripts/playout_controls.sh', '-c=getvolstep'], stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()
	result["idletime"] = subprocess.run(['../scripts/playout_controls.sh', '-c=getidletime'], stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()

	# fetch last card
	result["last_card"] = readfile(path + "/../settings/Latest_RFID")

	# fetch service states
	result["rfid"] = isServiceRunning("phoniebox-rfid-reader.service")
	result["gpio"] = isServiceRunning("phoniebox-gpio-buttons.service")

	# modify refresh rate depending on play state
	if result["state"] == "play":
		refreshInterval = refreshIntervalPlaying
	else:
		refreshInterval = refreshIntervalIdle

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
print("Subscribing to " + mqttBaseTopic + "/cmd/#")
client.subscribe(mqttBaseTopic + "/cmd/#")
print("Subscribing to " + mqttBaseTopic + "/get/#")
client.subscribe(mqttBaseTopic + "/get/#")

# start endless loop
client.loop_start()
while True:
	client.publish(mqttBaseTopic + "/get/all", payload="")
	time.sleep(refreshInterval)
