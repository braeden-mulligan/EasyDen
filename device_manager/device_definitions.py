from . import config

import re, sys, os

def read_device_defs():
	device_defs = os.path.dirname(__file__) + config.DEVICE_DEFINITIONS_PATH
	defs_file = open(device_defs, "r")
	contents = defs_file.read()
	defs_file.close()
	contents = re.sub("//.*?\n|/\*.*?\*/", "", contents, flags=re.S)
	contents = contents.split("\n")
	contents = [line.removeprefix("#define").strip() for line in contents if line.strip()]
	return contents

def build_definition_mapping(search_term):
	defs = read_device_defs()
	def_map = []
	for definition in defs:
		if search_term in definition:
			def_pair = definition.split(" ")
			reg = def_pair[0]
			index = def_pair[-1] # In case of multple spaces in line.
			def_map.append((reg, int(index)))
	return def_map

#TODO: Hashify these?
TYPE_MAP = build_definition_mapping("SH_TYPE_")
REGISTER_MAP = build_definition_mapping("_REG_")

CMD_NUL = 0
CMD_GET = 1
CMD_SET = 2
CMD_RSP = 3
CMD_PSH = 4
CMD_IDY = 5
#CMD_DAT = 6

def type_id(type_name):
	for t in TYPE_MAP:
		if (type_name == t[0]):
			return t[1]
	return None

def type_label(type_id):
	for t in TYPE_MAP:
		if type_id == t[1]:
			return t[0]
	return None

def register_id(reg_name):
	for reg in REGISTER_MAP:
		if reg_name == reg[0]:
			return reg[1]
	return None

# Because the register mapping is not one-to-one we need device type
# Type can be passed as either string or int
def register_label(reg_id, device_type):
	if isinstance(device_type, int):
		device_type = type_label(device_type)
	if not device_type:
		return None
	type_name = device_type.removeprefix("SH_TYPE_")

	for reg_label, reg_num in REGISTER_MAP:
		if reg_id == reg_num:
			if "GENERIC" in reg_label or type_name in reg_label:
				return reg_label
	return None
