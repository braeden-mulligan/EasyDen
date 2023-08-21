import socket

ENV = "development"

if socket.gethostname() == "easyden-server":
	ENV = "production"

DEVICE_DEFINITIONS_PATH = "/../libraries/common/device_definition.h"
DATABASE_PATH= "db/easyden.db"