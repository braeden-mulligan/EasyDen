# import sys
# sys.path.append("..")
# from common import device_definitions as dm_defs
# import common.device_messaging as interchange

# def register_id(label):
# 	return dm_defs.register_id(label)

import common.device_protocol_helpers as device_protocol
from common import device_definitions as device_defs

def repack_int_attribute(attribute_label, attributes):
	attribute = {}

	value = device_protocol.attribute_as_int(attribute_label, attributes)
	attr_id = device_defs.attribute_id(attribute_label)
	attribute = { "value": value, "id": attr_id }

	return attribute

def repack_float_attribute(attribute_label, attributes):
	attribute = {}

	value = device_protocol.attribute_as_float(attribute_label, attributes)
	if value == float("inf") or value == float("-inf"):
		value = None

	attr_id = device_defs.attribute_id(attribute_label)
	attribute = { "value": value, "id": attr_id }

	return attribute

def prune_device_data(device):
	del device["initialized"]
	del device["attributes"]

def build_command(command_data, integer_register_values = [], float_register_values = []):
	attr_id = int(command_data["attribute_id"])

	integer_register_values.append(device_defs.attribute_id("GENERIC_REG_ENABLE")),
	integer_register_values.append(device_defs.attribute_id("GENERIC_REG_RESET_CONFIGS"))

	if attr_id in float_register_values:
		value = float(command_data["value"])
		return device_protocol.build_command_from_float(attr_id, value)
	elif attr_id in integer_register_values:
		value = int(command_data["value"])
		return device_protocol.build_command_from_int(attr_id, value)

	return None

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