import sys
sys.path.append("..")

from common import defines
from common.log_handler import logger as log
from common import device_definitions as defs

import json, socket

def interconnect_transact(request_data, timeout = 1.0):
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

def fetch_devices(request_data): 
	query = {
		"entity": "device",
		"directive": "fetch",
		"parameters": request_data
	}

	device_type = request_data.get("type")

	if device_type:
		query["parameters"]["type"] = defs.device_type_id(device_type) if isinstance(device_type, str) else device_type

	return interconnect_transact(query)

def send_device_command(request_data, command_packet):
	query = {
		"entity": "device",
		"directive": "command",
		"parameters": request_data
	}

	query["parameters"]["command"] = command_packet

	return interconnect_transact(query)

# def submit_device_schedule(device_id, schedule_data):
# 	query = {
# 		"entity": "schedule",
# 		"directive": "create",
# 		"parameters": {
# 			"device-id": device_id,
# 			"schedule": schedule_data
# 		}
# 	}

# 	return message_transaction(query)

