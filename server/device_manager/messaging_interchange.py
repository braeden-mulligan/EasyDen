from . import device_definitions as SH_defs

import struct

_get = SH_defs.CMD_GET
_set = SH_defs.CMD_SET
_reg_id = SH_defs.register_id

template = "{:02X},{:02X},{:08X}" 

def _reg_id_parse(registers, reg_label = None, reg_id = None):
	reg_value_str = None
	try:
		if reg_label:
			reg_value_str = registers[str(_reg_id(reg_label))]["value"]

		elif reg_id:
			reg_value_str = registers[str(reg_id)]["value"]
	except KeyError:
		return None

	if reg_value_str:
		reg_value_str = reg_value_str.replace("0x", "")

	return reg_value_str

def reg_to_float(registers, reg_label = None, reg_id = None):
	reg_str = _reg_id_parse(registers, reg_label, reg_id)
	if reg_str:
		return struct.unpack("!f", bytes.fromhex(reg_str))[0]

	return None

def reg_to_int(registers, reg_label = None, reg_id = None):
	reg_str = _reg_id_parse(registers, reg_label, reg_id)
	if reg_str:
		return int(reg_str, 16)

	return None

def _map_to_register_id(reg):
	if isinstance(reg, str):
		return _reg_id(reg)
	elif isinstance(reg, int):
		return reg

	return None

def command_from_float(register, value):
	register_id = _map_to_register_id(register)
	if register_id is None:
		return None

	packed_float = struct.unpack("!I", struct.pack("!f", value))[0]
	return template.format(_set, register_id, packed_float);

def command_from_int(register, value):
	register_id = _map_to_register_id(register)
	if register_id is None:
		return None

	return template.format(_set, register_id, value);

def generic_request_identity():
	return template.format(SH_defs.CMD_IDY, 0, 0)

def generic_ping():
	return template.format(_get, _reg_id("GENERIC_REG_PING"), 0)


def poweroutlet_get_count():
	return template.format(_get, _reg_id("POWEROUTLET_REG_SOCKET_COUNT"), 0)

def poweroutlet_get_state():
	return template.format(_get, _reg_id("POWEROUTLET_REG_STATE"), 0)

# pass a list 
def poweroutlet_set_state(socket_states):
	high_byte = 0
	low_byte = 0
	for i, val in enumerate(socket_states):
		if val >= 0:
			high_byte |= (1 << i)
		if val > 0:
			low_byte |= (1 << i)
	reg_value = high_byte << 8 | low_byte
	print("REG VAL: " + str(reg_value))

	return template.format(_set, _reg_id("POWEROUTLET_REG_STATE"), reg_value)

# return list 
def poweroutlet_read_state(reg_value, socket_count = 8):
	if isinstance(reg_value, str):
		reg_value = int(reg_value, 16)

	if isinstance(socket_count, str):
		socket_count = int(socket_count, 16)

	if socket_count > 8:
		print("WARNING: poweroutlet_read_state invalid argument passed.")
		socket_count = 8

	socket_states = []

	for i in range(socket_count):
		if reg_value & (1 << i):
			socket_states.append(1)
		else:
			socket_states.append(0)

	return socket_states


def thermostat_get_temperature():
	return template.format(_get, _reg_id("THERMOSTAT_REG_TEMPERATURE"), 0)

def thermostat_get_target_temperature():
	return template.format(_get, _reg_id("THERMOSTAT_REG_TARGET_TEMPERATURE"), 0)

def thermostat_get_humidity():
	return template.format(_get, _reg_id("THERMOSTAT_REG_HUMIDITY"), 0)

def thermostat_set_temperature(value):
	#TODO: check value is float
	packed_float = struct.unpack("!i", struct.pack("!f", value))[0]
	return template.format(_set, _reg_id("THERMOSTAT_REG_TARGET_TEMPERATURE"), packed_float);
