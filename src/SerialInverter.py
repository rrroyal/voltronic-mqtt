import serial
import importlib
import ansi_codes as ansi
from fastcrc import crc16

def class_for_command(command: str) -> str:
	if command.startswith("POP"):
		return "ACK"
	
	return command

def class_for_name(module_name, class_name):
	m = importlib.import_module(module_name)
	c = getattr(m, class_name)
	return c

class SerialInverter:
	s = None

	def open(self, device_path: str, baudrate: int = 2400, bytesize: int = serial.EIGHTBITS, parity: str = serial.PARITY_NONE, stopbits: int = serial.STOPBITS_ONE):
		if self.s is not None and self.s.is_open:
			self.s.close()

		s = serial.Serial()
		s.port = device_path
		s.baudrate = baudrate
		s.bytesize = bytesize
		s.parity = parity
		s.stopbits = stopbits
		s.open()

		self.s = s

	def send_command(self, message: str, check_crc: bool = True):
		buf = b""

		message_bytes = bytes(message, "utf-8")
		crc = crc16.xmodem(message_bytes)

		buf += message_bytes
		buf += bytearray(crc.to_bytes(2, "big"))
		buf += bytearray(b"\r")

		self.s.write(buf)

		response = self.s.read_until(b"\r")

		if check_crc:
			response_content = response[:-3]
			response_crc = response[-3:-1]
			response_crc_calculated = crc16.xmodem(response_content).to_bytes(2, "big")

			if response_crc != response_crc_calculated:
				print(ansi.FG_RED + f"CRC mismatch! Response: {response_crc}, calculated: {response_crc_calculated}" + ansi.RESET)
				print(ansi.FG_CYAN + f"Content: {response_content}" + ansi.RESET)
				return

		return response

	def parse_response(self, command: str, response: str):
		try:
			klass = class_for_name("inverter_types", class_for_command(command))
			parsed = klass(response)
			return parsed
		except:
			return
