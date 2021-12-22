import re, sys, os

ENV = "development"

SERVER_ADDR = "0.0.0.0"
SERVER_PORT = 1338
DEVICE_MAX_CONN = 16

SERVER_INTERCONNECT = "/tmp/sh_server_ic"
DASHBOARD_MAX_CONN  = 2

POLL_TIMEOUT = 250
DEVICE_KEEPALIVE = 60

DEVICE_DEFINITIONS_PATH = "/../../libraries/common/device_definition.h"

if ENV == "production":
	BASE_DIR = "/root/server"
	#SERVER_ADDR = "192.168.1.85"
	DEBUG = False

elif ENV == "development":
	BASE_DIR = "/home/braeden/Projects/SmartHome/server"
	#SERVER_ADDR = "192.168.1.79"
	DEVICE_KEEPALIVE = 30
	DEBUG = True

else:
	raise ValueError("ENV not a valid option.")

def read_device_defs():
	device_defs = os.path.dirname(__file__) + DEVICE_DEFINITIONS_PATH
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

