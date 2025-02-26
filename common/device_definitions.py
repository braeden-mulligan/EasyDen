from . import defines

import re

class Device_Protocol:
	CMD_NUL = 0
	CMD_GET = 1
	CMD_SET = 2
	CMD_RSP = 3
	CMD_PSH = 4
	CMD_IDY = 5

IRRIGATION_MAX_SENSOR_COUNT = 3

def read_device_defs():
	device_defs = defines.DEVICE_DEFINITIONS_PATH
	defs_file = open(device_defs, "r")
	contents = defs_file.read()
	defs_file.close()
	contents = re.sub("//.*?\n|/\*.*?\*/", "", contents, flags=re.S)
	contents = contents.split("\n")
	contents = [line.removeprefix("#define").strip() for line in contents if line.strip()]
	return contents

def build_definition_mapping(search_term):
	defs = read_device_defs()
	def_map = {}
	for definition in defs:
		if search_term in definition:
			key, val = definition.split()
			def_map[key] = int(val, 16)
	return def_map

device_type_map = build_definition_mapping("DEVICE_TYPE_")
device_attribute_map = build_definition_mapping("_ATTR_")

def device_type_id(type_name):
	return device_type_map.get(type_name)

def device_type_label(type_id):
	for key, val in device_type_map.items():
		if val == type_id:
			return key
	return None

def attribute_id(attr_name):
	return device_attribute_map.get(attr_name)

# Because the register mapping is not one-to-one we need device type
# Type can be passed as either string or int
def attribute_label(attr_id, device_type):
	if isinstance(device_type, int):
		device_type = device_type_label(device_type)
	if not device_type:
		return None
	type_name = device_type.removeprefix("DEVICE_TYPE_")

	for attr_name, attr_num in device_attribute_map.items():
		if attr_num == attr_id:
			if "GENERIC" in attr_name or type_name in attr_name:
				return attr_name
	return None
