import device_manager.messaging_interchange as interchange
import device_manager.device_definitions as dm_defs

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
