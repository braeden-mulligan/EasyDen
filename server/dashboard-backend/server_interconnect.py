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

def fetch_devices(request_params = {}): 
	query = {
		"entity": "device",
		"directive": "fetch",
		"parameters": request_params
	}

	device_type = request_params.get("device-type")

	if device_type:
		query["parameters"]["device-type"] = defs.device_type_id(device_type) if isinstance(device_type, str) else device_type

	request_params["include-schedules"] = True

	return interconnect_transact(query)

def send_device_command(command_packet, request_params = {}):
	query = {
		"entity": "device",
		"directive": "command",
		"parameters": request_params
	}

	query["parameters"]["command"] = command_packet

	return interconnect_transact(query)
