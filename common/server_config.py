import socket 

ENV = "development"

if socket.gethostname() == "easyden-server":
	ENV = "production"

DASHBOARD_MAX_CONN  = 4
DEBUG = True
DEVICE_KEEPALIVE = 60
DEVICE_MAX_CONN = 32
MAX_TX_RETRIES = 2
POLL_TIMEOUT = 250
SERVER_PORT = 1338
TX_TIMEOUT = 3.0
TX_QUEUE_RETENTION_TIME = 86400.0 #-1.0
JWT_ACCESS_EXPIRY = 600
JWT_REFRESH_EXPIRY = 86400 * 30

if ENV == "production":
	pass

elif ENV == "development":
	DEVICE_KEEPALIVE = 45

else:
	raise ValueError("ENV not a valid option.")

