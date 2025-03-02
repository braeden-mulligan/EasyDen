# import sys
# sys.path.append("..")
# from common import device_definitions as dm_defs
# import common.device_messaging as interchange

# def register_id(label):
# 	return dm_defs.register_id(label)

import common.device_protocol_helpers as device_protocol
from common import device_definitions as device_defs

def unpack_attribute_to_int(attribute_label, attributes):
	attribute = {}

	value = device_protocol.reg_to_int(attributes, attribute_label)

	if value is not None:
		key = device_defs.attribute_id(attribute_label)
		attribute = { "value": value, "id": key }

	return attribute

def unpack_attribute_to_float(attribute_label, attributes):
	attr = unpack_attribute_to_int(attributes, attribute_label)

	attr["value"] = device_protocol.reg_to_float(attributes, attribute_label)

	if attr["value"] == float("inf") or attr["value"] == float("-inf"):
		attr["value"] = None

	return attr

def prune_device_data(device):
	#del device["type"]
	del device["initialized"]
	del device["attributes"]

# def build_command(attribute, integer_register_values = [], float_register_values = []):
# 	register = int(attribute["register"])

# 	integer_register_values.append(register_id("GENERIC_REG_ENABLE")),
# 	integer_register_values.append(register_id("GENERIC_REG_RESET_CONFIGS"))

# 	if register in float_register_values:
# 		value = float(attribute["attribute_data"])
# 		return interchange.build_command_from_float(register, value)
# 	elif register in integer_register_values:
# 		value = int(attribute["attribute_data"])
# 		return interchange.build_command_from_int(register, value)

# 	return None

# def reformat_schedules(device, processor):
# 	for i, schedule in enumerate(device["schedules"]):
# 		_, register, value = schedule.pop("command").split(',')
# 		register = int(register, 16)

# 		attribute = None
# 		if register == register_id("GENERIC_REG_ENABLE"):
# 			attribute = "enable"
# 			value = bool(int(value, 16))
# 		else:
# 			attribute, value = processor(register, value)

# 		device["schedules"][i]["attribute"] = attribute
# 		device["schedules"][i]["value"] = value