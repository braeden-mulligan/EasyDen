from .device import SH_Device

_get = SH_Device.CMD_GET
_set = SH_Device.CMD_SET
_reg = SH_Device.register_id

template = "{:02X},{:02X},{:08X}" 

def generic_request_identity():
	return template.format(SH_Device.CMD_IDY, 0, 0)

def generic_ping():
	return template.format(_get, _reg("GENERIC_REG_PING"), 0)

def poweroutlet_get_count():
	return template.format(_get, _reg("POWEROUTLET_REG_SOCKET_COUNT"), 0)

def poweroutlet_get_state():
	return template.format(_get, _reg("POWEROUTLET_REG_STATE"), 0)

# pass a list 
def poweroutlet_set_state(socket_states):
	high_byte = 0
	low_byte = 0
	for i, val in enumerate(socket_states):
		high_byte |= (1 << i)
		if val:
			low_byte |= (1 << i)
	reg_value = high_byte << 8 | low_byte
	print("REG VAL: " + str(reg_value))

	return template.format(_set, _reg("POWEROUTLET_REG_STATE"), reg_value)

# return list 
def poweroutlet_read_state(reg_value, socket_count = 8):
	if socket_count > 8:
		print("WARNING: poweroutlet_read_state invalid argument passed.")
		socket_count = 8

	if isinstance(reg_value, str):
		reg_value = int(reg_value, 16)
	socket_states = []

	for i in range(socket_count):
		if reg_value & (1 << i):
			socket_states.append(1)
		else:
			socket_states.append(0)

	return socket_states
