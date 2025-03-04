
import sys
sys.path.append("..")
from common.log_handler import logger as log, set_log_level_console, set_log_level_file

from device_manager import utilities as utils
from device_manager.device import SmartHome_Device

from database import operations as db

import json

def filter_devices(data, device_list, job_handler):
	devices = []

	for d in device_list:
		device_data = d.get_data()
		if data.get("include-meta-info"):
			device_data = {**device_data, "last-contact": d.last_contact, "reconnect-count": d.reconnect_count, "message-queue-retention-time": d.msg_queue_retention_time}

		if data.get("all"):
			devices.append(device_data)
		elif data.get("type") and d.device_type == data.get("type"):
			devices.append(device_data)
		elif data.get("id"):
			if isinstance(data.get("id"), list) and d.device_id in data.get("id"):
				devices.append(device_data) 
			elif d.device_id == data.get("id"):
				devices.append(device_data)
	
	if data.get("include-schedules"):
		for d in devices:
			d["schedules"] = job_handler.fetch_schedules(d["id"])

	return {
		"result": devices
	}

def send_device_command(data, device_list):
	devices = []

	for d in device_list:
		if data.get("all"):
			devices.append(d)
		elif data.get("type") and d.device_type == data.get("type"):
			devices.append(d)
		elif data.get("id") == d.device_id:
			devices.append(d)
	
	success = 0
	errors = []

	if not devices:
		return {
			"result": "No specified devices found"
		}

	for d in devices:
		result = d.device_send(data.get("command"))	
		if result == SmartHome_Device.ERROR_NO_SOCKET:
			errors.append({
				"code": "ERROR_NO_SOCKET",
				"details": "Device ID: " + str(d.device_id) + " has no socket connection."
			})
		elif result == SmartHome_Device.ERROR_QUEUE_FULL:
			errors.append({
				"code": "ERROR_QUEUE_FULL",
				"details": "Device ID: " + str(d.device_id) + " message queue is full somehow."
			})
		else:
			success += 1
			
	return {
		"result": "Command sent to " + str(success) + " devices",
		"error": errors
	}

def update_device_name(data, device_list):
	device = next((d for d in device_list if d.device_id == data.get("id")), None)
	if not device :
		return {
			"error": {
				"code": "DEVICE_NOT_FOUND",
				"details": "Device ID: " + str(data.get("id")) + " not found."
			}
		}

	device.name = data.get("name", device.name)
	db.update_device_name(device)

	return {
		"result": [device.get_data()]
	}

def _handle_dashboard_message(message, device_list, job_handler):
	log.info("Dashboard message: <" + str(message) + ">")

	params = message.get("parameters")

	if not params or not message.get("entity") or not message.get("directive"):
		return {
			"error": {
				"code": "INVALID_MESSAGE",
				"details": "Message missing field: entity, directive, or parameters"
			}
		}

	response = {
		"error": {
			"code": "UNKNOWN",
			"details": "Invalid message format"
		}
	}
	response_success = {
		"result": "success"
	}
	response_unimplemented = {
		"error": {
			"code": "UNIMPLEMENTED",
		}
	}
	
	match message:
		case { "entity": "device", "directive": "fetch" }:
			response = filter_devices(params, device_list, job_handler)
		case { "entity": "device", "directive": "command" }:
			response = send_device_command(params, device_list)
		case { "entity": "device", "directive": "update" }:
			response = update_device_name(params, device_list)

		case { "entity": "schedule", "directive": "fetch" }:
			response = response_unimplemented
		case { "entity": "schedule", "directive": "create" }:
			job_handler.submit_schedule(params.get("device-id"), params.get("schedule"))
			response = response_success
		case { "entity": "schedule", "directive": "delete" }:
			job_handler.submit_schedule(None, params.get("schedule"))
			response = response_success
		case { "entity": "schedule", "directive": "update" }:
			response = response_unimplemented
		
		case { "entity": "config", "directive": "fetch" }:
			response = response_unimplemented
		case { "entity": "config", "directive": "set" }:
			response = response_unimplemented
		
		case { "entity": "debug" }:
			response = response_unimplemented

	return response

def handle_dashboard_message(message, device_list, job_handler):
	message = json.loads(message)
	try:
		return json.dumps(_handle_dashboard_message(message, device_list, job_handler))
	except Exception as e:
		log.error("Error processing dashboard message.", exc_info = True)
		return json.dumps({
			"error": {
				"code": "UNHANDLED_EXCEPTION",
				"details": "Device manager: " + str(e)
			}
		})
