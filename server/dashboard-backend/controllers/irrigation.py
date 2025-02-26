import sys
sys.path.append("..")
from configs import device_definitions as dm_defs

from flask import request 

from dashboard import utilities as utils
from dashboard.controllers import base_device as base

import common.device_messaging as interchange

import json

FLOAT_REGISTER_VALUES = []

INTEGER_REGISTER_VALUES = [
	utils.register_id("IRRIGATION_REG_PLANT_ENABLE"),
	utils.register_id("IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_TIME"),
	utils.register_id("IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_AMOUNT"),
]

for i in range(dm_defs.IRRIGATION_MAX_SENSOR_COUNT):
	FLOAT_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_TARGET_MOISTURE_" + str(i)))
	FLOAT_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_MOISTURE_LOW_" + str(i)))
	INTEGER_REGISTER_VALUES.append(utils.register_id("IRRIGATION_REG_MOISTURE_LOW_DELAY_" + str(i)))

def irrigation_processor(irrigators):
	valid_devices = []
	for device in irrigators:
		if not device["initialized"]:
			continue

		sensor_count = utils.unpack_attribute(device["registers"], "IRRIGATION_REG_SENSOR_COUNT")
		enabled_plants = utils.unpack_attribute(device["registers"], "IRRIGATION_REG_PLANT_ENABLE")
		enabled_plants["value"] = interchange.irrigation_read_plant_enable(enabled_plants["value"], sensor_count["value"])
		calibration_mode = utils.unpack_attribute(device["registers"], "IRRIGATION_REG_CALIBRATION_MODE")
		calibration_plant_select = utils.unpack_attribute(device["registers"], "IRRIGATION_REG_CALIBRATION_MODE")
		calibration_mode["value"], calibration_plant_select["value"] = interchange.irrigation_read_calibration_settings(calibration_mode["value"])

		device["attributes"] = {
			"enabled": utils.unpack_attribute(device["registers"], "GENERIC_REG_ENABLE"),
			"reset_configs": 0,
			"sensor_count": sensor_count,
			"plant_enable": enabled_plants,
			"moisture_change_hysteresis_time": utils.unpack_attribute(device["registers"], "IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_TIME"),
			"moisture_change_hysteresis_amount": utils.unpack_attribute(device["registers"], "IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_AMOUNT"),
			"calibration_mode": calibration_mode,
			"calibration_plant_select": calibration_plant_select,
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

		utils.reformat_schedules(device, None)
		utils.prune_device_data(device)

		valid_devices.append(device)

	return valid_devices

def fetch(request):
	return base.fetch(request, irrigation_processor, "SH_TYPE_IRRIGATION")

def command(request):
	command_data = json.loads(request.data.decode())
	message = irrigation_build_command(command_data)

	if message:
		return base.command(request, command_data["register"], message, irrigation_processor, "SH_TYPE_IRRIGATION")
	
	return base.error({ "error": None })

def set_schedule(request):
	return base.set_schedule(request, utils.build_command, irrigation_processor, "SH_TYPE_IRRIGATION")

def irrigation_build_command(data):
	message = utils.build_command(data, INTEGER_REGISTER_VALUES, FLOAT_REGISTER_VALUES)

	if int(data["register"]) == utils.register_id("IRRIGATION_REG_CALIBRATION_MODE"):
		message = interchange.irrigation_set_calibration_settings(data["attribute_data"][0], data["attribute_data"][1])

	return message