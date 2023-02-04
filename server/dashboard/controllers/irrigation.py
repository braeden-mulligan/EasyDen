from flask import request 

from dashboard import utilities as utils
from dashboard.controllers import base_device as base

import device_manager.messaging_interchange as interchange

import json

FLOAT_REGISTER_VALUES = []

INTEGER_REGISTER_VALUES = [
	utils.register_id("GENERIC_REG_ENABLE"),
	utils.register_id("IRRIGATION_REG_SENSOR_COUNT"),
	utils.register_id("IRRIGATION_REG_PLANT_ENABLE"),
	utils.register_id("IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_TIME"),
	utils.register_id("IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_AMOUNT"),
	utils.register_id("IRRIGATION_REG_CALIBRATION_MODE"),
]

# TODO This number is based on irrigation device max sensor count.
for i in range(3):
	FLOAT_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_MOISTURE_" + str(i)))
	FLOAT_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_TARGET_MOISTURE_" + str(i)))
	FLOAT_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_MOISTURE_LOW_" + str(i)))
	
	INTEGER_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_MOISTURE_LOW_DELAY_" + str(i)))
	INTEGER_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_SENSOR_RAW_" + str(i)))
	INTEGER_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_SENSOR_RAW_MAX_" + str(i)))
	INTEGER_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_SENSOR_RAW_MIN_" + str(i)))
	INTEGER_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_SENSOR_RECORDED_MAX_" + str(i)))
	INTEGER_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_SENSOR_RECORDED_MIN_" + str(i)))


def irrigation_processor(irrigators):
	valid_devices = []
	for device in irrigators:
		if not device["initialized"]:
			continue

		sensor_count = utils.unpack_attribute(device["registers"], "IRRIGATION_REG_SENSOR_COUNT")
		enabled_plants = utils.unpack_attribute(device["registers"], "IRRIGATION_REG_PLANT_ENABLE")
		enabled_plants["value"] = interchange.irrigation_read_plant_enable(enabled_plants["value"], sensor_count["value"])

		device["attributes"] = {
			"enabled": utils.unpack_attribute(device["registers"], "GENERIC_REG_ENABLE"),
			"sensor_count": sensor_count,
			"plant_enable": enabled_plants,
			"moisture_change_hysteresis_time": utils.unpack_attribute(device["registers"], "IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_TIME"),
			"moisture_change_hysteresis_amount": utils.unpack_attribute(device["registers"], "IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_AMOUNT"),
			"calibration_mode": utils.unpack_attribute(device["registers"], "IRRIGATION_REG_CALIBRATION_MODE"),
			"moisture": [],
			"target_moisture": [],
			"moisture_low": [],
			"moisture_low_delay": [],
			"sensor_raw": [],
			"sensor_raw_max": [],
			"sensor_raw_min": [],
			"sensor_recorded_max": [],
			"sensor_recorded_min": [],
		}

		for i in range(device["attributes"]["sensor_count"]["value"]):
			device["attributes"]["moisture"].append(utils.unpack_attribute_to_float(device["registers"], "IRRIGATION_REG_MOISTURE_" + str(i)))
			device["attributes"]["target_moisture"].append(utils.unpack_attribute(device["registers"], "IRRIGATION_REG_TARGET_MOISTURE_" + str(i)))
			device["attributes"]["moisture_low"].append(utils.unpack_attribute(device["registers"], "IRRIGATION_REG_MOISTURE_LOW_" + str(i)))
			device["attributes"]["moisture_low_delay"].append(utils.unpack_attribute(device["registers"], "IRRIGATION_REG_MOISTURE_LOW_DELAY_" + str(i)))
			device["attributes"]["sensor_raw"].append(utils.unpack_attribute(device["registers"], "IRRIGATION_REG_SENSOR_RAW_" + str(i)))
			device["attributes"]["sensor_raw_max"].append(utils.unpack_attribute(device["registers"], "IRRIGATION_REG_SENSOR_RAW_MAX_" + str(i)))
			device["attributes"]["sensor_raw_min"].append(utils.unpack_attribute(device["registers"], "IRRIGATION_REG_SENSOR_RAW_MIN_" + str(i)))
			device["attributes"]["sensor_recorded_max"].append(utils.unpack_attribute(device["registers"], "IRRIGATION_REG_SENSOR_RECORDED_MAX_" + str(i)))
			device["attributes"]["sensor_recorded_min"].append(utils.unpack_attribute(device["registers"], "IRRIGATION_REG_SENSOR_RECORDED_MIN_" + str(i)))

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