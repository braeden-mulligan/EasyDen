import sys
sys.path.append("..")

from common.defines import *
from common.log_handler import logger as log
from common import device_definitions as defs
from common.utils import error_response

import json, socket

def interconnect_transact(request_data, timeout = 1.0):
	soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		soc.connect(SERVER_INTERCONNECT_PATH)
	except ConnectionRefusedError:
		log.debug("Connection refused:", exc_info = True )
		return error_response(E_SERVER_INTERCONNECT, "Device manager socket connection refused. Is the device manager running?")
	except Exception as e: 
		log.debug("Unhandled socket exception", exc_info = True)
		return error_response(E_SERVER_INTERCONNECT, "Device manager socket connection failed.", e)
	
	response = ""

	try:
		soc.settimeout(timeout)
		soc.send(json.dumps(request_data).encode())
		response = soc.recv(65536).decode()

		log.debug("Device manager response raw: " + response)

		soc.shutdown(socket.SHUT_RDWR)
		soc.close()
	except Exception as e:
		log.debug("Unhandled socket exception", exc_info = True)
		return error_response(E_SERVER_INTERCONNECT, "Device manager socket 'recv' failed.", e)

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

