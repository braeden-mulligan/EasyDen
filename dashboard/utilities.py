def prune_device_data(device):
	del device["type"]
	del device["initialized"]
	del device["registers"]
	return

def compose_response(response_label = None, data = None):
	if data is None:
		data = "Unknown error."
	if response_label is None:
		response_label = "ERROR"

	return response_label + ": " + data
