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
	#SERVER_ADDR = "192.168.1.69"
	DEBUG = False

elif ENV == "development":
	BASE_DIR = "/home/braeden/Projects/SmartHome/server"
	#SERVER_ADDR = "192.168.1.79"
	DEVICE_KEEPALIVE = 45
	DEBUG = True

else:
	raise ValueError("ENV not a valid option.")

