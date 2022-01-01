import module_manager 

import json, socket

SERVER_ERROR = -2
PARSE_ERROR = -1
RESPONSE_ERROR = 0
RESPONSE_SUCCESS = 1
RESPONSE_FAILURE = 2
RESPONSE_JSON = 3
RESPONSE_PARAMETER = 4

def strerror(errno):
	if errno == SERVER_ERROR:
		return "SERVER_ERROR"
	if errno == PARSE_ERROR:
		return "PARSE_ERROR"
	elif errno == RESPONSE_ERROR:
		return "RESPONSE_ERROR"
	elif errno == RESPONSE_SUCCESS:
		return "RESPONSE_SUCCESS"
	elif errno == RESPONSE_FAILURE:
		return "RESPONSE_FAILURE"
	elif errno == RESPONSE_JSON:
		return "RESPONSE_JSON"
	elif errno == RESPONSE_PARAMETER:
		return "RESPONSE_PARAMETER"

	return "UNKNOWN_ERROR"

def data_transaction(msg, timeout = 1.0):
	soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		soc.connect(module_manager.config.SERVER_INTERCONNECT)
	except ConnectionRefusedError as e:
		return "EXCEPTION: " + str(e)
	except Exception as e:
		return "EXCEPTION: " + str(e)
	
	soc.settimeout(timeout)

	soc.send(msg.encode())

	resp = ""
	try:
		resp = soc.recv(65536).decode()
		print("Dashboard got: " + resp)
	except Exception as e:
		resp = "EXCEPTION: " + str(e)
		print(e)

	soc.shutdown(socket.SHUT_RDWR)
	soc.close()

	return resp

def parse_response(transaction_result):
	response_package = (PARSE_ERROR, None)
	response_components = [item.strip() for item in transaction_result.split(':', 1)]

	if len(response_components) < 2:
		return (PARSE_ERROR, None)

	label = response_components[0]
	message = response_components[1]

	if "SUCCESS" in label:
		response_package = (RESPONSE_SUCCESS, message)
	elif "FAILURE" in label:
		response_package = (RESPONSE_FAILURE, message)
	elif "JSON" in label:
		json_message = json.loads(message)
		#TODO: Some error checking/validation here?
		response_package = (RESPONSE_JSON, json_message)
	elif "PARAMETER" in label:
		response_package = (RESPONSE_PARAMETER, message)
	elif "ERROR" in label: 
		response_package = (RESPONSE_ERROR, message)
	elif "EXCEPTION" in label:
		response_package = (SERVER_ERROR, message)

	return response_package

def compose_error_log(response_label, response_message):
	response_message = response_message.replace('EXCEPTION:', "Socket exception")
	error_log = "Module Manager response " + strerror(response_label) + ": " + str(response_message)
	return error_log

def device_command(device_id, message):
	return "command id " + str(device_id) + " " + message

def group_command(device_type, message):
	return "command type " + str(device_type) + " " + message

def server_command(message):
	return "command server " + message

