def prune_device_obj(device):
	del device["type"]
	del device["initialized"]
	del device["registers"]
	return
