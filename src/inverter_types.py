import enum

# https://github.com/ned-kelly/docker-voltronic-homeassistant/blob/master/manual/HS_MS_MSX_RS232_Protocol_20140822_after_current_upgrade.pdf

TEXT_ENCODING = "utf-8"

class QPI:
	protocol_id = None

	def __init__(self, raw_response: bytes):
		trimmed = raw_response[:-3]
		if not trimmed.startswith(b"(PI"):
			return
		if len(trimmed) != len("(PIXX"):
			return
		self.protocol_id = int(trimmed[3:])

class QID:
	serial_number = None

	def __init__(self, raw_response: bytes):
		trimmed = raw_response[:-3]
		if len(trimmed) != len("(XXXXXXXXXXXXXX"):
			return
		self.serial_number = int(trimmed[1:])

class QVFW:
	version = None

	def __init__(self, raw_response: bytes):
		trimmed = raw_response[:-3]
		if not trimmed.startswith(b"(VERFW:"):
			return
		self.version = trimmed[7:].decode(TEXT_ENCODING)

class QPIRI:
	grid_rating_voltage = None
	grid_rating_current = None
	ac_output_rating_voltage = None
	ac_output_rating_frequency = None
	ac_output_rating_current = None
	ac_output_rating_apparent_power = None
	ac_output_rating_active_power = None
	battery_rating_voltage = None
	battery_recharge_voltage = None
	battery_under_voltage = None
	battery_bulk_voltage = None
	battery_float_voltage = None
	battery_type = None
	current_max_ac_charging_current = None
	current_max_charging_current = None
	input_voltage_range = None
	output_source_priority = None
	charger_source_priority = None
	parallel_max_num = None
	machine_type = None
	topology = None
	output_mode = None
	battery_redischarge_voltage = None
	pv_ok_condition_for_parallel = None
	pv_power_balance = None

	class BatteryType(enum.IntEnum):
		AGM = 0
		Flooded = 1
		User = 2

	class InputVoltageRange(enum.IntEnum):
		Appliance = 0
		UPS = 1

	class OutputSourcePriority(enum.IntEnum):
		UtilityFirst = 0
		SolarFirst = 1
		SBUFirst = 2

	class ChargerSourcePriority(enum.IntEnum):
		UtilityFirst = 0
		SolarFirst = 1
		SolarAndUtility = 2
		OnlySolar = 3

	class MachineType(str, enum.Enum):
		GridTie = "00"
		OffGrid = "01"
		Hybrid = "10"

	class Topology(enum.IntEnum):
		TransformerLess = 0
		Transform = 1

	class OutputMode(enum.IntEnum):
		SingleMachine = 0
		Parallel = 1
		Phase1 = 2
		Phase2 = 3
		Phase3 = 4

	def __init__(self, raw_response: bytes):
		if not raw_response.startswith(b"("):
			return

		trimmed = raw_response[1:-3].decode(TEXT_ENCODING).split(" ")
		trimmed_len = len(trimmed)

		self.grid_rating_voltage = float(trimmed[0])
		self.grid_rating_current = float(trimmed[1])
		self.ac_output_rating_voltage = float(trimmed[2])
		self.ac_output_rating_frequency = float(trimmed[3])
		self.ac_output_rating_current = float(trimmed[4])
		self.ac_output_rating_apparent_power = int(trimmed[5])
		self.ac_output_rating_active_power = int(trimmed[6])
		self.battery_rating_voltage = float(trimmed[7])
		self.battery_recharge_voltage = float(trimmed[8])
		self.battery_under_voltage = float(trimmed[9])
		self.battery_bulk_voltage = float(trimmed[10])
		self.battery_float_voltage = float(trimmed[11])
		self.battery_type = QPIRI.BatteryType(int(trimmed[12]))
		self._something1 = trimmed[13]
		self._something2 = trimmed[14]
		self.input_voltage_range = QPIRI.InputVoltageRange(int(trimmed[15]))
		self.output_source_priority = QPIRI.OutputSourcePriority(int(trimmed[16]))
		self.charger_source_priority = QPIRI.ChargerSourcePriority(int(trimmed[17]))
		self.parallel_max_num = int(trimmed[18])
		self.machine_type = QPIRI.MachineType(trimmed[19])
		self.topology = QPIRI.Topology(int(trimmed[20]))
		self.output_mode = QPIRI.OutputMode(int(trimmed[21]))
		self.battery_redischarge_voltage = float(trimmed[22])
		self.pv_ok_condition_for_parallel = trimmed[23]
		self.pv_power_balance = trimmed[24]
		self._something3 = trimmed[25] if trimmed_len > 25 else None
		self._something4 = trimmed[26] if trimmed_len > 26 else None
		self._something5 = trimmed[27] if trimmed_len > 27 else None

class QFLAG:
	silence_buzzer = None
	overload_bypass = None
	power_saving = None
	lcd_timeout = None
	overload_restart = None
	over_temperature_restart = None
	backlight = None
	alarm_on_primary_source_interrupt = None
	fault_code_record = None

	def __init__(self, raw_response: bytes):
		if not raw_response.startswith(b"("):
			return

		trimmed = raw_response[1:-3]
		split = trimmed.decode(TEXT_ENCODING).split("D")
		enabled = split[0][1:]
		disabled = split[1]

		self.silence_buzzer = "a" in enabled
		self.overload_bypass = "b" in enabled
		self.power_saving = "j" in enabled
		self.lcd_timeout = "k" in enabled
		self.overload_restart = "u" in enabled
		self.over_temperature_restart = "v" in enabled
		self.backlight = "x" in enabled
		self.alarm_on_primary_source_interrupt = "y" in enabled
		self.fault_code_record = "z" in enabled

class QPIGS:
	grid_voltage = None
	grid_frequency = None
	ac_output_voltage = None
	ac_output_frequency = None
	ac_output_apparent_power = None
	ac_output_active_power = None
	output_load_percent = None
	bus_voltage = None
	battery_voltage = None
	battery_charging_current = None
	battery_capacity = None
	inverter_heatsink_temperature = None
	pv_input_current = None
	pv_input_voltage = None
	battery_voltage_scc = None
	battery_discharge_current = None
	device_status_1 = None
	battery_voltage_offset_for_fans_on = None
	eeprom_version = None
	pv_charging_power = None
	device_status_2 = None

	def __init__(self, raw_response: bytes):
		if not raw_response.startswith(b"("):
			return

		trimmed = raw_response[1:-3]
		[
			grid_voltage,
			grid_frequency,
			ac_output_voltage,
			ac_output_frequency,
			ac_output_apparent_power,
			ac_output_active_power,
			output_load_percent,
			bus_voltage,
			battery_voltage,
			battery_charging_current,
			battery_capacity,
			inverter_heatsink_temperature,
			pv_input_current,
			pv_input_voltage,
			battery_voltage_scc,
			battery_discharge_current,
			device_status_1,
			battery_voltage_offset_for_fans_on,
			eeprom_version,
			pv_charging_power,
			device_status_2
		] = trimmed.decode(TEXT_ENCODING).split(" ")

		self.grid_voltage = float(grid_voltage)
		self.grid_frequency = float(grid_frequency)
		self.ac_output_voltage = float(ac_output_voltage)
		self.ac_output_frequency = float(ac_output_frequency)
		self.ac_output_apparent_power = int(ac_output_apparent_power)
		self.ac_output_active_power = int(ac_output_active_power)
		self.output_load_percent = int(output_load_percent)
		self.bus_voltage = int(bus_voltage)
		self.battery_voltage = float(battery_voltage)
		self.battery_charging_current = int(battery_charging_current)
		self.battery_capacity = int(battery_capacity)
		self.inverter_heatsink_temperature = int(inverter_heatsink_temperature)
		self.pv_input_current = float(pv_input_current)
		self.pv_input_voltage = float(pv_input_voltage)
		self.battery_voltage_scc = float(battery_voltage_scc)
		self.battery_discharge_current = float(battery_discharge_current)
		self.device_status_1 = device_status_1	# TODO
		self.battery_voltage_offset_for_fans_on = int(battery_voltage_offset_for_fans_on)
		self.eeprom_version = eeprom_version	# TODO
		self.pv_charging_power = int(pv_charging_power)
		self.device_status_2 = device_status_2	# TODO

class QMOD:
	mode = None

	class DeviceMode(str, enum.Enum):
		PowerOn = "P"
		Standby = "S"
		Line = "L"
		Battery = "B"
		Fault = "F"
		PowerSaving = "H"

	def __init__(self, raw_response: bytes):
		if not raw_response.startswith(b"("):
			return

		trimmed = raw_response[1:-3]
		self.mode = QMOD.DeviceMode(trimmed.decode(TEXT_ENCODING))

class ACK:
	success = None

	def __init__(self, raw_response: bytes):
		self.success = raw_response.startswith(b'(ACK')
