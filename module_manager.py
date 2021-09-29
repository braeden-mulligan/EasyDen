import select, socket, sys, time, os

DASHBOARD_MAX_CONN  = 2
SERVER_INTERCONNECT = "/tmp/sh_server_ic"

DEVICE_MAX_CONN = 16
#WIFI_HOST = "192.168.0.105"
WIFI_HOST = "0.0.0.0"
WIFI_PORT = 1338

POLL_TIMEOUT = 1000

def dashboard_conn_init():
	if os.path.exists(SERVER_INTERCONNECT):
		os.remove(SERVER_INTERCONNECT)

	soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	soc.setblocking(False)
	soc.bind(SERVER_INTERCONNECT)
	soc.listen(DASHBOARD_MAX_CONN)
	return soc

def device_conn_init():
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	soc.setblocking(False)
	soc.bind((WIFI_HOST, WIFI_PORT))
	soc.listen(DEVICE_MAX_CONN)
	return soc

#device_map = {}

if __name__ == "__main__":
	poller = select.poll()

	dash_soc = dashboard_conn_init()
	device_soc = device_conn_init()
	dashboard_connections = []
	device_connections = []

	poll_opts = select.POLLIN | select.POLLERR | select.POLLHUP
	poller.register(dash_soc, poll_opts)
	poller.register(device_soc, poll_opts)

	while True:
		poll_result = poller.poll(POLL_TIMEOUT)

		for fd, event in poll_result:
			print("FD: " + str(fd) + " EVENT: " + str(event))

			if (fd == dash_soc.fileno()):
				conn, addr = dash_soc.accept()
				dashboard_connections.append(conn)
				print("Dashboard connected from " + str(addr))
				#poller.register(conn, select.POLLIN | select.POLLERR)

			elif (fd == device_soc.fileno()):
				conn, addr = device_soc.accept()
				device_connections.append(conn)
				print("Device connected from " + str(addr))
				#register new device

			"""
			else:
				if event == hup:
					deregister fd
				else:
					for dash_connect in dash_conns:	
						recv etc.
					for device in device_conns
						recv etc.
			"""

