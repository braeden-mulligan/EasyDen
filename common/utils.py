# Devices that have multiple binary i/o channels for an attribute map bits from lowest byte to determine state.
# To control which channels to toggle, set the corresponding bit of high byte. Else consider low byte bit null.
def list_to_bitmask(value_list):
	high_byte = 0
	low_byte = 0

	for i, val in enumerate(value_list):
		if val >= 0:
			high_byte |= (1 << i)
		if val > 0:
			low_byte |= (1 << i)

	reg_value = high_byte << 8 | low_byte

	return reg_value


def bitmask_to_list(value, item_count):
	value_list = []

	for i in range(item_count):
		if value & (1 << i):
			value_list.append(1)
		else:
			value_list.append(0)

	return value_list