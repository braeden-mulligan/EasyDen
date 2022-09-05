def prune_device_data(device):
	del device["type"]
	del device["initialized"]
	del device["registers"]
	return
