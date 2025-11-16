import sys
sys.path.append("..")

from common.defines import *
from common.utils import error_response
from common import server_config as config
from .. import server_interconnect as interconnect
import common.device_protocol_helpers as device_protocol
from common import device_definitions as device_defs

import time

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

def fetch(request_params, device_data_processor):
	response = interconnect.fetch_devices(request_params)

	if response.get("result") is not None:
		response["result"] = device_data_processor(response["result"])
		return response

	if response.get("error") is None:
		return error_response()
	
	return response

# NOTE: Only supports one device at a time for now
def command(request_params, command_packet, device_data_processor):
	response = interconnect.send_device_command(command_packet, request_params)

	if response.get("error"):
		return response

	timeout = time.monotonic() + (request_params.get("timeout") or (config.TX_TIMEOUT * (config.MAX_TX_RETRIES  + 1) + 1.0))

	while time.monotonic() < timeout:
		time.sleep(0.15)
		devices = interconnect.fetch_devices(request_params).get("result")
		if not devices:
			continue 

		target_attribute = int(command_packet.split(",")[1], 16)

		last_query = devices[0]["attributes"].get(str(target_attribute), {}).get("queried_at")
		last_update = devices[0]["attributes"].get(str(target_attribute), {}).get("updated_at")

		if last_query is None or last_update is None:
			continue

		if last_update > last_query:
			return {
				"result": device_data_processor(devices)
			}

	return error_response(E_TIMEOUT, "Device response could not be confirmed.")

