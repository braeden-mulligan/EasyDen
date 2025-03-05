from pathlib import Path

DATABASE_PATH = str(Path(__file__).parent.parent) + "/server/database/easyden.db"
DEVICE_DEFINITIONS_PATH = str(Path(__file__).parent.parent) + "/device-firmware/libraries/common/device_definition.h"
SERVER_INTERCONNECT_PATH = "/tmp/sh_server_ic"

E_DEVICE = "DEVICE_ERROR"
E_INVALID_REQUEST = "INVALID_REQUEST"
E_REQUEST_FAILED = "REQUEST_FAILED"
E_SERVER_INTERCONNECT = "SERVER_INTERCONNECT"
E_TIMEOUT = "TIMEOUT"
E_UNIMPLEMENTED = "UNIMPLEMENTED"
E_UNKNOWN = "UNKNOWN_ERROR"
