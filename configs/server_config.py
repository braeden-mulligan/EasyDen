from . import common_config as cfg

SERVER_ADDR = "0.0.0.0"
SERVER_PORT = 1338

SERVER_INTERCONNECT = "/tmp/sh_server_ic"

DASHBOARD_MAX_CONN  = 2
DEVICE_MAX_CONN = 16

POLL_TIMEOUT = 250
DEVICE_KEEPALIVE = 60
DEVICE_MAX_TX_RETRIES = 2
DEVICE_TX_TIMEOUT = 3.0
DEVICE_TX_QUEUE_RETENTION_TIME = 86400.0 #-1.0

if cfg.ENV == "production":
	SERVER_ADDR = "192.168.1.69"
	DEBUG = False

elif cfg.ENV == "development":
	SERVER_ADDR = "192.168.1.71"
	DEVICE_KEEPALIVE = 45
	DEBUG = True

else:
	raise ValueError("ENV not a valid option.")

