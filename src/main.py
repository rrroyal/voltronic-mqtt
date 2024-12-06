import argparse
import time
import json
import enum
import ansi_codes as ansi
from serial import SerialException
from SerialInverter import SerialInverter
from MqttClient import MqttClient

class VerboseLevel(int, enum.Enum):
	Never = -2
	Always = -1
	Silent = 0
	Error = 1
	Notice = 2
	Info = 3
	Debug = 4

VERBOSE = VerboseLevel.Silent
PROCESSING_COMMAND = False

def log(level: VerboseLevel, msg: str):
	if VERBOSE >= level:
		print(msg)

def parse_mqtt_param(param: str):
	split = param.strip().split("@")
	split_len = len(split)

	username = None
	password = None
	host = None
	port = None

	if split_len == 0:
		return None
	elif split_len == 1:
		# only host
		[url] = split
		[host, port] = url.split(":")
	elif split_len == 2:
		# user + pass + host
		[passwd, url] = split
		[username, password] = passwd.split(":")
		[host, port] = url.split(":")

	return [
		username,
		password,
		host,
		int(port) if port is not None else None
	]

def send_mqtt_update(mqtt_client: MqttClient, mqtt_topic: str, payload: str):
	log(VerboseLevel.Debug, ansi.FG_CYAN + f"Sending payload..." + ansi.RESET)
	[success, return_code] = mqtt_client.send_message(mqtt_topic, payload, retain=False)
	if success == True:
		log(VerboseLevel.Debug, ansi.FG_CYAN + f"Sent payload!" + ansi.RESET)
	else:
		log(VerboseLevel.Error, ansi.FG_RED + f"Failed to update: {return_code}" + ansi.RESET)

def process_command(inverter_client: SerialInverter, command: str):
	log(VerboseLevel.Info, ansi.FG_MAGENTA + f"Requesting \"{command}\"..." + ansi.RESET)

	data = inverter_client.send_command(command, check_crc=False)
	if data is None:
		log(VerboseLevel.Error, ansi.FG_RED + f"Didn't get data in response!" + ansi.RESET)
		return

	parsed = inverter_client.parse_response(command, data)

	log(VerboseLevel.Debug, ansi.FG_YELLOW + str(data) + ansi.RESET)

	if parsed is not None:
		parsed_json = json.dumps(parsed.__dict__)
		log(VerboseLevel.Info, parsed_json)
		return parsed_json
	else:
		log(VerboseLevel.Error, ansi.FG_RED + f"Failed to parse!\n{data}" + ansi.RESET)
		return None

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("command", help="comma-separated commands to send")
	parser.add_argument("-d", "--device", type=str, help=f"serial device", dest="serial_device", required=True)
	parser.add_argument("-p", "--polling-interval", type=int, help="Polling interval", dest="polling_interval")
	parser.add_argument("-m", "--mqtt", help="mqtt config (format: <username>:<password>@<broker>:<port>)", dest="mqtt_credentials")
	parser.add_argument("-c", "--client-id", help=f"mqtt client id", dest="mqtt_client_id")
	parser.add_argument("-t", "--topic", help=f"mqtt topic", dest="mqtt_topic")
	parser.add_argument("-s", "--subscribe-topic", help=f"mqtt topic to subscribe to", dest="mqtt_topic_sub")
	parser.add_argument("-v", "--verbose", help="verbose level", type=int, dest="verbose_level", default=VerboseLevel.Silent)
	args = parser.parse_args()

	global VERBOSE
	VERBOSE = VerboseLevel(args.verbose_level)

	commands = args.command.split(",")

	mqtt_client = None
	mqtt_credentials: str | None = args.mqtt_credentials
	mqtt_client_id: str | None = args.mqtt_client_id
	mqtt_topic: str | None = args.mqtt_topic
	if mqtt_credentials is not None and mqtt_client_id is not None and mqtt_topic is not None:
		mqtt_parsed = parse_mqtt_param(mqtt_credentials)
		if mqtt_parsed is not None:
			[mqtt_username, mqtt_password, mqtt_broker, mqtt_port] = mqtt_parsed
			mqtt_client = MqttClient(mqtt_client_id, mqtt_username, mqtt_password)
			mqtt_client.connect(mqtt_broker, mqtt_port)

	serial_device = args.serial_device.strip()

	log(VerboseLevel.Info, ansi.FG_CYAN + f"Opening \"{serial_device}\"..." + ansi.RESET)
	inverter_client = SerialInverter(device_path = serial_device)
	inverter_client.open()

	def process(command: str, send_mqtt_message: bool = True):
		global PROCESSING_COMMAND
		while PROCESSING_COMMAND:
			pass

		PROCESSING_COMMAND = True
		output_json = process_command(inverter_client, command)
		PROCESSING_COMMAND = False

		if send_mqtt_message and mqtt_client is not None and output_json is not None:
			topic = f"{mqtt_topic}/{command}".lower()
			send_mqtt_update(mqtt_client, topic, output_json)

	if mqtt_client is not None and args.mqtt_topic_sub is not None:
		topic = f"{mqtt_topic}/{args.mqtt_topic_sub}".lower()
		log(VerboseLevel.Notice, ansi.FG_CYAN + f"Subscribing to \"{topic}\"" + ansi.RESET)

		def handle_mqtt_message(userdata, msg):
			command = msg.payload.decode()
			log(VerboseLevel.Notice, ansi.FG_CYAN + f"Incoming message: \"{command}\"" + ansi.RESET)
			process(command, send_mqtt_message=False)

		mqtt_client.subscribe(topic, handle_mqtt_message)

	if args.polling_interval is None:
		# oneshot
		for command in commands:
			process(command)
	else:
		# loop
		while True:
			try:
				for command in commands:
					process(command)
			except SerialException as e:
				log(VerboseLevel.Error, ansi.FG_RED + f"{e.strerror}" + ansi.RESET)
				inverter_client.open()
			finally:
				time.sleep(args.polling_interval)

if __name__ == "__main__":
	main()
