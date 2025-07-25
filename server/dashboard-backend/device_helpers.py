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
	attr_id = int(command_data["attribute-id"])

	integer_register_values.append(device_defs.attribute_id("GENERIC_ATTR_ENABLE")),
	integer_register_values.append(device_defs.attribute_id("GENERIC_ATTR_RESET_CONFIGS"))
	integer_register_values.append(device_defs.attribute_id("GENERIC_ATTR_BLINK"))

	if attr_id in float_register_values:
		value = float(command_data["attribute-value"])
		return device_protocol.build_command_from_float(attr_id, value)
	elif attr_id in integer_register_values:
		value = int(command_data["attribute-value"])
		return device_protocol.build_command_from_int(attr_id, value)

	return None

def repack_schedule(schedule, processor):
	_, attr, value = schedule.get("command").split(',')
	attr = int(attr, 16)
	value = int(value, 16)

	attribute_name = None

	if attr == device_defs.attribute_id("GENERIC_ATTR_ENABLE"):
		attribute_name = "enable"
		value = bool(value)

	else:
		attribute_name, value = processor(attr, value)

	schedule["command"] = {
		"attribute_name": attribute_name,
		"value": value
	}