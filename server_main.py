if __name__ == "__main__":
	from module_manager import socket_server
	socket_server.run()

else:
	import os, sys

	dir_path = os.path.dirname(os.path.realpath(__file__))
	sys.path.append(dir_path)

	from dashboard import dashboard_app

