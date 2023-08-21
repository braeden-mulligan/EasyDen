import sys
sys.path.append("..")
from configs import server_config as config

from device_manager.device import SmartHome_Device
from device_manager import messaging_interchange as messaging
from device_manager import utilities as utils
from device_manager.jobs import Nexus_Jobs
from db import operations as db

import json, select, socket, time, os, logging

device_list = []
dashboard_connections = []
job_handler = None


# --- Socket Management ---

def listener_init(dashboard = False):
	addr_fam = socket.AF_INET
	addr = ("0.0.0.0", config.SERVER_PORT)
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

def socket_close(soc, poll_obj):
	try:
		poll_obj.unregister(soc)
		soc.shutdown(socket.SHUT_RDWR)
		soc.close()
	except Exception as e:
		utils.print_exception(e)
	return True

def handle_socket_error(soc, event, poll_obj):
	if event & select.POLLHUP or event & select.POLLERR: 
		return socket_close(soc, poll_obj)
	return False


# --- Device Messaging Tools ---

def device_from_identifier(soc_fd = -1, device_id = -1):
	for d in device_list:
		if soc_fd == d.soc_fd:
			return d
		if device_id == d.device_id:
			return d
	return None

def handle_device_message(device):
	recv_code = device.device_recv()

	if recv_code < 0:
		return False

	# If we have a positive recv_code that is a device id returned from an identity request.
	elif recv_code > 0: # ID detected, check for duplicate devices
		db.add_device(device)

		for existing_device in device_list:
			if recv_code == existing_device.device_id and device is not existing_device:
				# We have an already existing entry with this id. This would happen if a device drops and reconnects.
				# Update old entry with new socket and delete current device object.
				existing_device.connect(device.soc_connection)
				existing_device.pending_response = None
				print("Existing device found with id " + str(recv_code))
				device_list.remove(device)

	return True


# --- Dashboard Messaging ---

def handle_dashboard_message(dash_conn, msg):
	response = "ERROR: Malformed request"

	# if not utils.dashboard_message_validate(msg):
	# 	dash_conn.send(response.encode())
	# 	return
		
	print("Dashboard message: [" + msg + "]")
	
	words = msg.split(' ')

	# fetch [all | type <int> | id <int>]
	if "fetch" in words[0]:
		obj_list = None

		if "all" in words[1]:
			obj_list = [d.get_data() for d in device_list if d.device_id]
		elif "type" in words[1]:
			obj_list = [d.get_data() for d in device_list if d.device_type == int(words[2])]
		elif "id" in words[1]:
			obj_list = [d.get_data() for d in device_list if d.device_id == int(words[2])]
		
		for entry in obj_list:
			entry["schedules"] = job_handler.fetch_schedules(entry["id"])

			if "registers" not in entry:
				continue

			utils.hexify_attribute_values(entry["registers"])

		if isinstance(obj_list, list):
			response = "JSON: " + json.dumps(obj_list)

	# command [id|type <int> <raw message>]
	elif "command" in words[0]:
		if "id" in words[1]:
			d = device_from_identifier(device_id = int(words[2]));
			if d:
				d.device_send(words[3])
				response = "SUCCESS: Command sent"
			else:
				response = "ERROR: Device not found"

		elif "type" in words[1]:
			device_count = 0
			d_type = int(words[2])
			for d in device_list:
				if d.device_type == d_type:
					d.device_send(words[3])
					device_count += 1
			if device_count: 
				response = "SUCCESS: command sent to " + str(device_count) + " devices"
			else:
				response = "ERROR: No devices found"
		
		elif "server" in words[1]:
			pass

	# info [id <int> <specifier> | type <int> <specifier>]
	elif "info" in words[0]:
		if "id" in words[1]:
			device = next((d for d in device_list if d.device_id == int(words[2])), None)

			if device is None:
				response = "ERROR: Device not found"
			elif "last_contact" in words[3]:
				response = "PARAMETER: " + str(device.last_contact)
			elif "reconnections" in words[3]:
				response = "PARAMETER: " + str(device.reconnect_count)
			elif "fully_initialized" in words[3]:
				response = "PARAMETER: " + str(device.fully_initialized).lower()	
		elif "type" in words[1]:
			pass	
		elif "server" in words[1]:
			if "schedules" in words[2]:
				response = "SUCCESS: " + str(["Device " + str(s.device_id) + " " + str(s.job) for s in jobs.schedules])

	elif "rename" in words[0]:
		d = device_from_identifier(device_id = int(words[1]))
		d.name = " ".join(words[2:])
		db.update_device_name(d)
		response = "SUCCESS: New name for device " + str(d.device_id) + " " + d.name

	elif "schedule" in words[0]:
		data = "".join(words[2:])
		job_handler.submit_schedule(int(words[1]), data)
		response = "SUCCESS: Schedule submitted"

	elif "debug" in words[0]:
		response = "FAILURE: Unimplemented feature"
		
	dash_conn.send(response.encode())
	return

# --- ---

def main_loop():
	global device_list

	def device_entry_loader(db_row):
		device = SmartHome_Device()
		device.device_id, device.device_type, device.name = db_row
		device_list.append(device)

	db.load_devices(device_entry_loader)
	print("Devices loaded")
	print([d.get_data() for d in device_list])

	global job_handler
	job_handler = Nexus_Jobs(device_list)

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
				if not d.device_send(messaging.generic_request_identity()):
					print("New device failed to respond")
					socket_close(d.soc_connection, poller)
					device_list.remove(d)

		poll_result = poller.poll(config.POLL_TIMEOUT)

		for fd, event in poll_result:
			if event & select.POLLNVAL:
				poller.unregister(fd)

			elif (fd == dash_soc.fileno()):
				conn, addr = dash_soc.accept()
				conn.setblocking(False)
				poller.register(conn, poll_opts)
				dashboard_connections.append(conn)

			elif (fd == device_soc.fileno()):
				conn, addr = device_soc.accept()
				conn.setblocking(False)
				poller.register(conn, poll_opts)
				device_list.append(SmartHome_Device(conn))

			else:
				dash_conn = next((d for d in dashboard_connections if d.fileno() == fd), None)
				if dash_conn is not None:
					if handle_socket_error(dash_conn, event, poller):
						dashboard_connections.remove(dash_conn)
					else:
						handle_dashboard_message(dash_conn, dash_conn.recv(2048).decode())
				# else:
				device = device_from_identifier(fd)
				if device is not None:
					if handle_socket_error(device.soc_connection, event, poller):
						print("Device disconnected.")
						# Socket now closed so set device to disconnected. 
						device.disconnect() # But do not remove device from list.
					elif not handle_device_message(device):
#TODO: Decide what to do depending how handle_device_message fails
						socket_close(device.soc_connection, poller)
						device.disconnect() 
					print(" ")

		for d in device_list:
			device_status = d.update_pending()
			
			if device_status == SmartHome_Device.STATUS_UNRESPONSIVE:
				print("Device " + str(d.device_id) + " unresponsive. Closing connection")
			elif device_status == SmartHome_Device.STATUS_ERROR:
				print("Device " + str(d.device_id) + " socket error handled. Closing connection")
			
			if device_status != SmartHome_Device.STATUS_OK:
				handle_socket_error(d.soc_connection, select.POLLHUP, poller)
				d.disconnect()

		job_handler.run_tasks()

def run():
	log_dir = os.path.dirname(__file__) + "/logs"
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)
	logging.basicConfig(filename=log_dir + "/device_manager.log", level = logging.DEBUG, format = "[%(asctime)s %(levelname)s %(name)s %(message)s] : ")
	logger = logging.getLogger(__name__)

	try:
		print("Starting device manager.")
		main_loop()
	except KeyboardInterrupt:
		raise
	except:
		print("Caught unhandled exception. Check logs for details.")
		logging.exception("Device manager crashed!")
		raise
