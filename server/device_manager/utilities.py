def hexify_attribute_values(attributes):
	for reg in attributes:
		attributes[reg]["value"] = "0x{:08X}".format(attributes[reg]["value"])

