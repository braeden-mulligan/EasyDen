import device_manager 

import json, socket

def data_transaction(msg, timeout = 1.0):
	soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		soc.connect(device_manager.config.SERVER_INTERCONNECT)
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
	response_package = ("ERROR", "Dashboard failed to parse message from device manager.")
	response_components = [item.strip() for item in transaction_result.split(':', 1)]

	if len(response_components) < 2:
		return response_package

	response_label = response_components[0]
	data = response_components[1] or "null"

	if response_label == "JSON":
		json_data = json.loads(data)
		#TODO: Some error checking/validation here?
		response_package = (response_label, json_data)
	else:
		response_package = (response_label, data)

	return response_package

def fetch_devices(device_id = None, device_type = None):
	query = "fetch "
	if device_id:
		query += "id " + str(device_id)
	elif device_type:
		query += "type " + str(device_type)
	else:
		query += "all"

	response = data_transaction(query)

	return parse_response(response)

def device_command(device_id, message):
	return "command id " + str(device_id) + " " + message

def group_command(device_type, message):
	return "command type " + str(device_type) + " " + message

def server_command(message):
	return "command server " + message

