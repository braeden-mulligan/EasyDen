from .device import SH_Device

_get = SH_Device.CMD_GET
_set = SH_Device.CMD_SET

template = "{:02X},{:02X},{:08X}" 

def generic_request_identity():
	return template.format(SH_Device.CMD_IDY, 0, 0)

def poweroutlet_get_count():
	return template.format(_get, SH_Device.POWEROUTLET_REG_OUTLET_COUNT, 0)

def poweroutlet_get_state():
	return template.format(_get, SH_Device.POWEROUTLET_REG_STATE, 0)

# pass a list of tuples (<outlet index>, <boolean value>)
def poweroutlet_set_state(outlet_values):
	reg = SH_Device.POWEROUTLET_REG_STATE
	high_byte = 0
	low_byte = 0
	for i, val in outlet_values:
		high_byte |= (1 << i)
		if val:
			low_byte |= (1 << i)
		else:
			low_byte &= ~(1 << i)
	reg_value = high_byte << 8 | low_byte

	return template.format(_set, SH_Device.POWEROUTLET_REG_STATE, reg_value)

