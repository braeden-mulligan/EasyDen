import sys
sys.path.append("..")

from common import defines
from common.log_handler import logger as log
from common import device_definitions as defs

import json, socket

def message_transaction(request_data, timeout = 1.0):
	soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		soc.connect(defines.SERVER_INTERCONNECT_PATH)
	except ConnectionRefusedError as e:
		log.debug("Connection refused:", exc_info = True )
		return {
			"error": {
				"code": "CONNECTION_REFUSED",
				"details": "Device manager socket connection failed. Is the device manager running?"
			}
		}
	except: 
		log.debug("Unhandled socket exception", exc_info = True)
		return {
			"error": {
				"code": "UNKNOWN",
				"details": "Device manager socket connection failed."
			}
		}
	
	response = ""

	try:
		soc.settimeout(timeout)
		soc.send(json.dumps(request_data).encode())
		response = soc.recv(65536).decode()

		log.debug("Device manager response raw: " + response)

		soc.shutdown(socket.SHUT_RDWR)
		soc.close()
	except:
		log.debug("Unhandled socket exception", exc_info = True)
		return {
			"error": {
				"code": "UNKNOWN",
				"details": "Device manager socket 'recv' failed."
			}
		}

	return json.loads(response)

def fetch_devices(device_id = None, device_type = None, meta_info = None):
	query = {
		"category": "device",
		"directive": "fetch",
		"parameters": {}
	}

	if device_id:
		query["parameters"]["id"] = device_id
	elif device_type:
		query["parameters"]["type"] = defs.device_type_id(device_type) if isinstance(device_type, str) else device_type
	else:
		query["parameters"]["all"] = True

	if meta_info:
		query["parameters"]["include-meta-info"] = meta_info

	return message_transaction(query)

def send_device_command(device_id, command_packet):
	query = {
		"category": "device",
		"directive": "command",
		"parameters": {
			"id": device_id,
			"command": command_packet 
		}
	}

	return message_transaction(query)

# def submit_device_schedule(device_id, schedule_data):
# 	query = {
# 		"category": "schedule",
# 		"directive": "create",
# 		"parameters": {
# 			"device-id": device_id,
# 			"schedule": schedule_data
# 		}
# 	}

# 	return message_transaction(query)

