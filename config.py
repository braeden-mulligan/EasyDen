DEBUG = False

BASE_DIR = None
if ENVIRONMENT == "dev":
	BASE_DIR = "/root"
elif ENVIRONMENT == "prod":
	BASE_DIR = ""
