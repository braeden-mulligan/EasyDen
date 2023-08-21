import sys
sys.path.append("..")
from configs import device_definitions as dm_defs

import device_manager.messaging_interchange as interchange

def register_id(label):
	return dm_defs.register_id(label)

def unpack_attribute(registers, register_label):
	attribute = {}

	value = interchange.reg_to_int(registers, register_label)

	if value is not None:
		key = str(dm_defs.register_id(register_label))
		attribute = { "value": value, "register": key }

	return attribute

def unpack_attribute_to_float(registers, reg_label):
	attr = unpack_attribute(registers, reg_label)
	attr["value"] = interchange.reg_to_float(registers, reg_label)
	if attr["value"] == float("inf") or attr["value"] == float("-inf"):
		attr["value"] = None
	return attr

def prune_device_data(device):
	del device["type"]
	del device["initialized"]
	del device["registers"]
	return

def compose_response(response_label = None, data = None):
	if data is None:
		data = "Unknown error."
	if response_label is None:
		response_label = "ERROR"

	return response_label + ": " + data

def build_command(attribute, integer_register_values = [], float_register_values = []):
	register = int(attribute["register"])

	integer_register_values.append(register_id("GENERIC_REG_ENABLE")),
	integer_register_values.append(register_id("GENERIC_REG_RESET_CONFIGS"))

	if register in float_register_values:
		value = float(attribute["attribute_data"])
		return interchange.build_command_from_float(register, value)
	elif register in integer_register_values:
		value = int(attribute["attribute_data"])
		return interchange.build_command_from_int(register, value)

	return None

def reformat_schedules(device, processor):
	for i, schedule in enumerate(device["schedules"]):
		_, register, value = schedule.pop("command").split(',')
		register = int(register, 16)

		attribute = None
		if register == register_id("GENERIC_REG_ENABLE"):
			attribute = "enable"
			value = bool(int(value, 16))
		else:
			attribute, value = processor(register, value)

		device["schedules"][i]["attribute"] = attribute
		device["schedules"][i]["value"] = value