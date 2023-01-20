from flask import request 

from dashboard import utilities as utils
from dashboard.controllers import base_device as base

import device_manager.messaging_interchange as interchange

import json

FLOAT_REGISTER_VALUES = [
	utils.register_id("IRRIGATION_REG_MOISTURE_0"),
	utils.register_id("IRRIGATION_REG_MOISTURE_1"),
	utils.register_id("IRRIGATION_REG_MOISTURE_2")
]

INTEGER_REGISTER_VALUES = [
	utils.register_id("GENERIC_REG_ENABLE"),
	utils.register_id("IRRIGATION_REG_SENSOR_COUNT"),
]

def irrigation_processor(irrigators):
	valid_devices = []
	for device in irrigators:
		if not device["initialized"]:
			continue

		device["attributes"] = {}

		device["attributes"]["enabled"] = utils.unpack_attribute(device["registers"], "GENERIC_REG_ENABLE")
		device["attributes"]["sensor_count"] = utils.unpack_attribute(device["registers"], "IRRIGATION_REG_SENSOR_COUNT")

		device["attributes"]["moisture"] = [ utils.unpack_attribute_to_float(device["registers"], "IRRIGATION_REG_MOISTURE_0") ]
		device["attributes"]["sensor_raw"] = [ utils.unpack_attribute(device["registers"], "IRRIGATION_REG_SENSOR_RAW_0") ]
		# Assuming at least one sensor exists
		if device["attributes"]["sensor_count"]["value"] > 1:
			device["attributes"]["moisture"].append(utils.unpack_attribute_to_float(device["registers"], "IRRIGATION_REG_MOISTURE_1"))
			device["attributes"]["sensor_raw"].append(utils.unpack_attribute(device["registers"], "IRRIGATION_REG_SENSOR_RAW_1"))
		if device["attributes"]["sensor_count"]["value"] > 2:
			device["attributes"]["moisture"].append(utils.unpack_attribute_to_float(device["registers"], "IRRIGATION_REG_MOISTURE_2")) 
			device["attributes"]["sensor_raw"].append(utils.unpack_attribute(device["registers"], "IRRIGATION_REG_SENSOR_RAW_2"))

		# for i, schedule in enumerate(device["schedules"]):
		# 	tag = schedule
		# 	_, register, value = tag["command"].split(',')
		# 	register = int(register, 16)

		# 	if register == utils.register_id("IRRIGATION_REG_TARGET_MOISTURE_0"):
		# 		target_moisture = [ interchange.reg_to_float({ str(register): { "value": value }}, reg_id = register) ]
		# 	else:
		# 		continue

		# 	device["schedules"][i] = { "attribute": "target_moisture", "value": target_moisture, "id_tag": tag }

		utils.prune_device_data(device)
		valid_devices.append(device)

	return valid_devices

def fetch(request):
	return base.fetch(request, irrigation_processor, "SH_TYPE_IRRIGATION")

def build_command(request_data):
	register = int(request_data["register"])

	if register in FLOAT_REGISTER_VALUES:
		value = float(request_data["data"])
		return interchange.command_from_float(register, value)
	elif register in INTEGER_REGISTER_VALUES:
		value = int(request_data["data"])
		return interchange.command_from_int(register, value)

	return None

def command(request):
	command_data = json.loads(request.data.decode())
	message = build_command(command_data)

	if message:
		return base.command(request, command_data["register"], message, irrigation_processor, "SH_TYPE_IRRIGATION")
	
	return base.error({ "error": None })


def set_schedule(request):
	schedule_data = json.loads(request.data.decode())
	
	if schedule_data["action"] == "create":
		message = build_command(schedule_data)
		del schedule_data["register"]
		del schedule_data["data"]

		schedule_data["command"] = message
	elif schedule_data["action"] == "delete":
		pass

	return base.set_schedule(request, json.dumps(schedule_data), irrigation_processor, "SH_TYPE_IRRIGATION")