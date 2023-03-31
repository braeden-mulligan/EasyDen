ENV = "development"

SERVER_ADDR = "0.0.0.0"
SERVER_PORT = 1338
DEVICE_MAX_CONN = 16

SERVER_INTERCONNECT = "/tmp/sh_server_ic"
DASHBOARD_MAX_CONN  = 2

POLL_TIMEOUT = 250
DEVICE_KEEPALIVE = 60
DEVICE_MAX_TX_RETRIES = 2
DEVICE_TX_TIMEOUT = 3.0
DEVICE_TX_QUEUE_RETENTION_TIME = 86400.0 #-1.0

DEVICE_DEFINITIONS_PATH = "/../../libraries/common/device_definition.h"
DATABASE_PATH="db/easyden.db"

if ENV == "production":
	BASE_DIR = "/root/server"
	DEBUG = False

elif ENV == "development":
	BASE_DIR = "/home/braeden/Projects/EasyDen/server"
	DEVICE_KEEPALIVE = 45
	DEBUG = True

else:
	raise ValueError("ENV not a valid option.")

