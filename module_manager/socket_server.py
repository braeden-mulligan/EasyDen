from . import config
from .device import SH_Device
from .messaging import *

import json, select, socket, sys, time, os

device_list = []
dashboard_connections = []

# --- Socket Management ---

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

# --- ---


# --- Device Messaging Tools ---

def device_from_attr(soc_fd = -1, device_id = -1):
	for d in device_list:
		if soc_fd == d.soc_fd:
			return d
		if device_id == d.device_id:
			return d
	return None

def handle_device_message(device, new_id):
	if new_id: # Check for duplicate devices
		for existing_device in device_list:
			if new_id == existing_device.device_id and device is not existing_device:
				# We have an already existing entry with this id
				# Update old entry with new socket and delete current device object
				existing_device.connect(device.soc_connection)
				existing_device.pending_response = None
				print("Duplicate device found with id " + str(new_id))
				device_list.remove(device)
	return 

# --- ---


# --- Dashboard Messaging ---

#TODO: improve upon cursory validation
def dashboard_message_validate(msg):
	if not msg:
		return False

	words = msg.split(' ')
	if len(words) < 2: 
		return False

	if "fetch" in words[0]:
		if "all" in words[1]:
			pass
		elif len(words) < 3:
			return False

	elif "command" in words[0]:
		if len(words) < 3:
			return False

		if "id" in words[1]:
			if len(words) < 4:
				return False

			cmd = words[3].split(',')
			if len(cmd) < 3:
				return False

		elif "server" in words[1] and len(words) < 3:
			return False

	elif "info" in words[0]:
		if "id" in words[1] and len(words) < 4:
			return False
		elif "server" in words[1] and len(words) < 3:
			return False

	return True
		
#TODO: web server expects ACK
def handle_dashboard_message(dash_conn, msg):
	response = "ERROR: Malformed request"

	if not dashboard_message_validate(msg):
		dash_conn.send(response.encode())
		return
		
	print("Dash message: [" + msg + "]")
	words = msg.split(' ')

# fetch [all | type x | id x]
	if "fetch" in words[0]:
		json_obj_list = []

		if "all" in words[1]:
			json_obj_list = [d.get_obj_json() for d in device_list if d.device_id]
			response = "JSON: " + json.dumps(json_obj_list)
		elif "type" in words[1]:
			#TODO: validate
			num = int(words[2])
			json_obj_list = [d.get_obj_json() for d in device_list if d.device_type == num]
			response = "JSON: " + json.dumps(json_obj_list)
		elif "id" in words[1]:
			#TODO: validate
			num = int(words[2])
			json_obj_list = [d.get_obj_json() for d in device_list if d.device_id == num]
			response = "JSON: " + json.dumps(json_obj_list)

# command [id x <raw message> | server <specifier>]
	elif "command" in words[0]:
		response = "SUCCESS: null"

		if "id" in words[1]:
			d_id = int(words[2])
			d = device_from_attr(device_id = d_id);
			if d:
				d.device_send(words[3])
			else:
				response = "ERROR: Device not found"
		elif "server" in words[1]:
			# set <device id> name <name>
			response = "FAILURE: Unimplemented feature"

# info [id x <specifier> | server <specifier>]
	elif "info" in words[0]:
		if "id" in words[1]:
			#TODO: validate
			num = int(words[2])
			device = next((d for d in device_list if d.device_id == num), None)

			if device is None:
				response = "ERROR: Device not found"
			elif "last_contact" in words[3]:
				response = "PARAMETER: " + str(device.last_contact)
			elif "reconnections" in words[3]:
				response = "PARAMETER: " + str(device.reconnect_count)

		elif "server" in words[1]:
			response = "FAILURE: Unimplemented feature"

	elif "debug" in words[1]:
		response = "FAILURE: Unimplemented feature"
		
	dash_conn.send(response.encode())
	return

# --- ---


def run():
	print("Starting socket server.")
	poller = select.poll()

	dash_soc = listener_init(dashboard = True)
	device_soc = listener_init()

	poll_opts = select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL
	poller.register(dash_soc, poll_opts)
	poller.register(device_soc, poll_opts)

	while True:
		for d in device_list:
			if not d.device_id and d.pending_response is None:
				print("New device detected, requesting ID")
				d.device_send(generic_request_identity())

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
			d.check_heartbeat()

		#for d in device_list:
			#d.initial_connection_task()			

		# other routine checks.
		# ...

