from .device import SH_Device

_get = SH_Device.CMD_GET
_set = SH_Device.CMD_SET
_reg = SH_Device.register_id

template = "{:02X},{:02X},{:08X}" 

def generic_request_identity():
	return template.format(SH_Device.CMD_IDY, 0, 0)

def poweroutlet_get_count():
	return template.format(_get, _reg("POWEROUTLET_REG_OUTLET_COUNT"), 0)

def poweroutlet_get_state():
	return template.format(_get, _reg("POWEROUTLET_REG_STATE"), 0)

# pass a list of tuples (<outlet index>, <boolean value>)
def poweroutlet_set_state(outlet_values):
	high_byte = 0
	low_byte = 0
	for i, val in outlet_values:
		high_byte |= (1 << i)
		if val:
			low_byte |= (1 << i)
		else:
			low_byte &= ~(1 << i)
	reg_value = high_byte << 8 | low_byte

	return template.format(_set, _reg("POWEROUTLET_REG_STATE"), reg_value)

# return list of tuples (<outlet index>, <boolean value>)
def poweroutlet_read_state(reg_value, outlet_count = 8):
	if outlet_count > 8:
		print("WARNING: poweroutlet_read_state invalid argument passed.")
		outlet_count = 8

	reg_value = int(reg_value, 16)
	outlets = []

	for i in range(outlet_count):
		if reg_value & (1 << i):
			outlets.append((i, True))
		else:
			outlets.append((i, False))

	return outlets
