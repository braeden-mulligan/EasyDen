
import sys
sys.path.append("..")
from common.log_handler import logger as log, set_log_level_console, set_log_level_file
from common.defines import *
from common.utils import error_response

from device_manager.device import SmartHome_Device

from database import operations as db

import json

def filter_devices(params, device_list, job_handler):
	devices = []

	for d in device_list:
		device_data = d.get_data()
		if params.get("include-meta-info"):
			device_data = {**device_data, "last-contact": d.last_contact, "reconnect-count": d.reconnect_count, "message-queue-retention-time": d.msg_queue_retention_time}

		if params.get("device-id"):
			if isinstance(params.get("device-id"), list) and d.id in params.get("device-id"):
				devices.append(device_data) 
			elif d.id == params.get("device-id"):
				devices.append(device_data)
		elif params.get("device-type") and d.type == params.get("device-type"):
			devices.append(device_data)
		elif params.get("all"):
			devices.append(device_data)
	
	if params.get("include-schedules"):
		for d in devices:
			d["schedules"] = job_handler.fetch_schedules(d["id"])

	return {
		"result": devices
	}

def send_device_command(params, device_list):
	devices = []

	for d in device_list:
		if params.get("device-id"):
			if isinstance(params.get("device-id"), list) and d.id in params.get("device-id"):
				devices.append(d) 
			elif d.id == params.get("device-id"):
				devices.append(d)
		elif params.get("device-type") and d.type == params.get("device-type"):
			devices.append(d)
		elif params.get("all"):
			devices.append(d)
	
	success = 0
	errors = []

	if not devices:
		return {
			"result": "No specified devices found"
		}

	for d in devices:
		result = d.device_send(params.get("command"))	
		if result == SmartHome_Device.ERROR_NO_SOCKET:
			errors.append(error_response(E_DEVICE, "Device ID: " + str(d.id) + " has no socket connection."))
		elif result == SmartHome_Device.ERROR_QUEUE_FULL:
			errors.append(error_response(E_DEVICE, "Device ID: " + str(d.id) + " message queue is full somehow."))
		else:
			success += 1
			
	return {
		"result": "Command sent to " + str(success) + " devices",
		"error": errors
	}

def update_device_name(data, device_list):
	device = next((d for d in device_list if d.id == data.get("device-id")), None)
	if not device :
		return error_response(E_DEVICE, "Device ID: " + str(data.get("device-id")) + " not found.")

	device.name = data.get("name", device.name)
	db.update_device_name(device)

	return {
		"result": [device.get_data()]
	}

def _handle_dashboard_message(message, device_list, job_handler):
	log.info("Dashboard message: <" + str(message) + ">")

	params = message.get("parameters")

	if not message.get("entity") or not message.get("directive"):
		return error_response(E_INVALID_REQUEST, "Dashboard message missing field: entity or directive")

	response = error_response()
	response_unimplemented = error_response(E_UNIMPLEMENTED)
	
	match message:
		case { "entity": "device", "directive": "fetch" }:
			return filter_devices(params, device_list, job_handler)
		case { "entity": "device", "directive": "command" }:
			return send_device_command(params, device_list)
		case { "entity": "device", "directive": "update" }:
			return update_device_name(params, device_list)

		case { "entity": "schedule", "directive": "fetch" }:
			return response_unimplemented
		case { "entity": "schedule", "directive": "create" }:
			return job_handler.create_schedule(params.get("device-id"), params.get("schedule"))
		case { "entity": "schedule", "directive": "delete" }:
			return job_handler.delete_schedule(params.get("schedule-id"))
		case { "entity": "schedule", "directive": "update" }:
			return response_unimplemented
		
		case { "entity": "server", "directive": "config-get" }:
			return response_unimplemented
		case { "entity": "server", "directive": "config-set" }:
			if "name" in params and "device-id" in params:
				update_device_name(params, device_list)
			return response_unimplemented
		
		case { "entity": "debug" }:
			return response_unimplemented

	return response

def handle_dashboard_message(message, device_list, job_handler):
	message = json.loads(message)
	try:
		return json.dumps(_handle_dashboard_message(message, device_list, job_handler))
	except Exception as e:
		log.exception("Error processing dashboard message.")
		return json.dumps(error_response(E_UNKNOWN, "Device manager undandled exception.", e))
