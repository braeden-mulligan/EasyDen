def prune_device_data(device):
	del device["type"]
	del device["initialized"]
	del device["registers"]
	return

def compose_response(response_label = None, data = None):
	if not data:
		data = "Unknown error."
	if not response_label:
		response_label = "ERROR"

	return response_label + ": " + data
