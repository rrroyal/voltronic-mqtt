# import json
import ansi_codes as ansi
import paho.mqtt.client as mqtt

PUBLISH_TIMEOUT = 5

class MqttClient:
	client = None
	message_queue = []

	def __init__(self, client_id: str, username: str, password: str):
		self.client = mqtt.Client(client_id, protocol=mqtt.MQTTv5)
		self.client.username_pw_set(username, password)

	def connect(self, broker: str, port: int):
		def on_connect(client, userdata, flags, rc, _):
			if rc != 0:
				print(ansi.FG_RED + f"Failed to connect, return code: {rc}" + ansi.RESET)

		self.client.on_connect = on_connect
		self.client.connect(broker, port)
		self.client.loop_start()

		while not self.client.is_connected():
			pass

	def subscribe(self, topic: str, handler: any):
		def on_message(client, userdata, msg):
			handler(userdata, msg)

		self.client.subscribe(topic)
		self.client.on_message = on_message

	def send_message(self, topic: str, message: str, retain: bool = False):
		result = self.client.publish(topic, message, qos=2, retain=retain)
		result.wait_for_publish(PUBLISH_TIMEOUT)
		return_code = result[0]
		# self.handle_return_code(return_code)

		return (return_code == mqtt.MQTT_ERR_SUCCESS, return_code)

	# def handle_return_code(self, errno: int):
	# 	if errno != mqtt.MQTT_ERR_SUCCESS:
	# 		error_message = mqtt.error_string(errno)
	# 		print(ansi.FG_RED + f"{error_message} ({errno})" + ansi.RESET)

	# 		if errno == mqtt.MQTT_ERR_NO_CONN:
	# 			self.client.reconnect()
