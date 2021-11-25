ENV = "development"

SERVER_ADDR = "0.0.0.0"
SERVER_PORT = 1338
DEVICE_MAX_CONN = 16

SERVER_INTERCONNECT = "/tmp/sh_server_ic"
DASHBOARD_MAX_CONN  = 2

POLL_TIMEOUT = 250
DEVICE_KEEPALIVE = 60

if ENV == "production":
	BASE_DIR = "/root/server"
	SERVER_ADDR = "192.168.1.85"
	DEBUG = False

elif ENV == "development":
	BASE_DIR = "/home/braeden/Projects/SmartHome/server"
	SERVER_ADDR = "192.168.1.79"
	DEVICE_KEEPALIVE = 30
	DEBUG = True

else:
	raise ValueError("ENV not a valid option.")

