from . import config
from .device import SH_Device
import json, select, socket, sys, time, os

device_list = []
dashboard_connections = []

def listener_init(dashboard = False):
	addr_fam = socket.AF_INET
	addr = (config.SERVER_ADDR, config.SERVER_PORT)
	max_conn = config.DEVICE_MAX_CONN
	if dashboard:
		if os.path.exists(config.SERVER_INTERCONNECT):
			os.remove(config.SERVER_INTERCONNECT)
		addr_fam = socket.AF_UNIX
		addr = config.SERVER_INTERCONNECT
		max_conn = config.DASHBOARD_MAX_CONN

	soc = socket.socket(addr_fam, socket.SOCK_STREAM)
	soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	soc.setblocking(False)
	soc.bind(addr)
	soc.listen(max_conn)
	return soc

def socket_error(soc, event, poll_obj):
	if event & select.POLLHUP or event & select.POLLERR: 
		print("Unregister fd " + str(soc.fileno()))
		poll_obj.unregister(soc)
		try:
			soc.shutdown(socket.SHUT_RDWR)
		except Exception as err:
			print(err)
		soc.close()
		return True
	return False

def device_from_attr(soc_fd = -1, device_id = -1):
	for d in device_list:
		if soc_fd == d.soc_fd:
			return d
		if device_id == d.device_id:
			return d
	return None

def handle_dashboard_message(dash_conn, msg):
	print("Dash message: [" + msg + "]")
#TODO: debugging stuff here
	if "fetch" in msg:
		json_obj_list = []
		for d in device_list:
			if d.device_id:
				json_obj_list.append(d.get_json_obj())
		dash_conn.send(json.dumps(json_obj_list).encode())
	elif "debug get" in msg:
		d_id = int(msg.split(' ')[2])
		d = device_from_attr(device_id = d_id);
		if d:
			d.device_send(SH_Device.CMD_GET, SH_Device.POWEROUTLET_REG_STATE, 0)
	elif "debug set" in msg:
		d_id = int(msg.split(' ')[2])
		val = int(msg.split(' ')[3])
		val = 0xFFFF if val else 0xFF00
		d = device_from_attr(device_id = d_id);
		if d:
			d.device_send(SH_Device.CMD_SET, SH_Device.POWEROUTLET_REG_STATE, val)
	return

def handle_device_message(device, new_id):
	if new_id: # Check for duplicate devices
		for existing_device in device_list:
			if new_id == existing_device.device_id and device is not existing_device:
				# We have an already existing entry with this id
				# Update old entry with new socket and invalidate current device
				existing_device.connect(device.soc_connection)
				existing_device.pending_response = None
				print("Duplicate device found with id " + str(new_id))
				print("Old device list" + str (device_list))
				device_list.remove(device)
				print("Removed device " + str(device))
				print("Updated device list" + str (device_list))
	return 

#if __name__ == "__main__":
def run():
	print("Starting socket server.")
	poller = select.poll()

	dash_soc = listener_init(dashboard = True)
	device_soc = listener_init()

#TODO POLLOUT?
	poll_opts = select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL
	poller.register(dash_soc, poll_opts)
	poller.register(device_soc, poll_opts)

	while True:
		for d in device_list:
			if not d.device_id and d.pending_response is None:
				print("New device detected, requesting ID")
				d.device_send(SH_Device.CMD_IDY, 0, 0)

		poll_result = poller.poll(config.POLL_TIMEOUT)

		for fd, event in poll_result:
			print("\nFD: " + str(fd) + " EVENT: " + str(event))

			if event & select.POLLNVAL:
				print("Unregister fd " + str(fd))
				poller.unregister(fd)

			elif (fd == dash_soc.fileno()):
				conn, addr = dash_soc.accept()
				conn.setblocking(False)
				print("Dashboard connected from " + str(addr))
				poller.register(conn, poll_opts)
				dashboard_connections.append(conn)

			elif (fd == device_soc.fileno()):
				conn, addr = device_soc.accept()
				conn.setblocking(False)
				print("Device connected from " + str(addr))
				poller.register(conn, poll_opts)
				device_list.append(SH_Device(conn))

			else:
				dash_conn = next((d for d in dashboard_connections if d.fileno() == fd), None)
				if dash_conn is not None:
					if socket_error(dash_conn, event, poller):
						dashboard_connections.remove(dash_conn)
					else:
						handle_dashboard_message(dash_conn, dash_conn.recv(2048).decode())
				# else:
				device = device_from_attr(fd)
				if device is not None:
					print("Device operation fd: " + str(device.soc_fd))
					if socket_error(device.soc_connection, event, poller):
						print("Device disconnected.")
						device.disconnect() # But do not remove device from list.
					else:
						handle_device_message(device, device.device_recv())
					print(" ")

		for d in device_list:
			if d.update_pending() == SH_Device.STATUS_UNRESPONSIVE and d.no_response >= 2:
				print("Device " + str(d.device_id) + " unresponsive. Closing connection")
				socket_error(d.soc_connection, select.POLLHUP, poller)
				d.disconnect()

		for d in device_list:
			d.check_keepalive()

		# other routine checks.
		# ...

