import sys, time
sys.path.append("..")
from common import server_config as config
from common import utils 
from common import device_protocol_helpers
from common.log_handler import logger as log, init_log_file
from common.mailer import send_email

from device_manager.device import SmartHome_Device
from device_manager.jobs import Nexus_Jobs
from device_manager.dashboard_messaging import handle_dashboard_message

from database import operations as db

import select, socket, os 

dashboard_connections = []
device_list = []
job_handler = None


def listener_init(dashboard = False):
	addr_fam = socket.AF_INET
	addr = ("0.0.0.0", config.SERVER_PORT)
	max_conn = config.DEVICE_MAX_CONN
	if dashboard:
		if os.path.exists(utils.get_abs_path("device_manager_interconnect")):
			os.remove(utils.get_abs_path("device_manager_interconnect"))
		addr_fam = socket.AF_UNIX
		addr = utils.get_abs_path("device_manager_interconnect")
		max_conn = config.DASHBOARD_MAX_CONN

	soc = socket.socket(addr_fam, socket.SOCK_STREAM)
	soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	soc.setblocking(False)

	bind_attempts = 0
	bind_attempt_limit = 3

	while bind_attempts < bind_attempt_limit:
		bind_attempts += 1

		try:
			soc.bind(addr)
			break
		except OSError as e:
			if e.errno == 98 and bind_attempts < bind_attempt_limit:
				log.error(repr(e))
			else:
				raise

			time.sleep(30)

	soc.listen(max_conn)
	return soc

def socket_close(soc, poll_obj):
	try:
		poll_obj.unregister(soc)
		soc.shutdown(socket.SHUT_RDWR)
		soc.close()
	except OSError as e:
		if e.errno == 107:
			log.info("Exception trying to close socket.", exc_info = True)
	except:
		log.warning("Exception trying to close socket.", exc_info = True)
	return True

def handle_socket_error(soc, event, poll_obj):
	if event & select.POLLHUP or event & select.POLLERR: 
		if next((conn for conn in dashboard_connections if conn.fileno() == soc), None) is not None:
			log.info("Device socket error event: POLLHUP" if event & select.POLLHUP else "POLLERR")
		return socket_close(soc, poll_obj)
	return False


def device_from_identifier(soc_fd = -1, device_id = -1):
	for d in device_list:
		if soc_fd == d.soc_fd or device_id == d.id:
			return d
	return None

def handle_device_message(device):
	recv_code = device.device_recv()

	if recv_code < 0:
		return False

	# If we have a positive recv_code that is a device id returned from an identity request.
	elif recv_code > 0:
		db.add_device(device)

		for existing_device in device_list:
			if recv_code == existing_device.id and device is not existing_device:
				# We have an already existing entry with this id. This would happen if a device drops and reconnects.
				# Update old entry with new socket and delete current device object.
				log.debug("Existing device found with id " + str(recv_code))
				existing_device.connect(device.soc_connection)
				existing_device.pending_response = None
				device_list.remove(device)

	return True

def main_loop():
	global device_list
	global job_handler

	def device_entry_loader(db_row):
		device = SmartHome_Device()
		device.id, device.type, device.name = db_row
		device_list.append(device)

	db.load_devices(device_entry_loader)
	log.debug("Devices loaded " + str([d.get_data() for d in device_list]))

	job_handler = Nexus_Jobs(device_list)

	poller = select.poll()

	dash_soc = listener_init(dashboard = True)
	device_soc = listener_init()

	poll_opts = select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL
	poller.register(dash_soc, poll_opts)
	poller.register(device_soc, poll_opts)

	while True:
		for d in device_list:
			if not d.id and d.pending_response is None:
				log.info("New device detected, requesting ID")
				if d.device_send(device_protocol_helpers.generic_request_identity()) <= 0:
					log.info("New device failed to respond")
					socket_close(d.soc_connection, poller)
					device_list.remove(d)

		poll_result = poller.poll(config.POLL_TIMEOUT)

		for fd, event in poll_result:
			if event & select.POLLNVAL:
				poller.unregister(fd)

			elif (fd == dash_soc.fileno()):
				conn, _ = dash_soc.accept()
				conn.setblocking(False)
				poller.register(conn, poll_opts)
				dashboard_connections.append(conn)

			elif (fd == device_soc.fileno()):
				conn, _ = device_soc.accept()
				conn.setblocking(False)
				poller.register(conn, poll_opts)
				device_list.append(SmartHome_Device(conn))

			else:
				dash_conn = next((conn for conn in dashboard_connections if conn.fileno() == fd), None)
				if dash_conn is not None:
					if handle_socket_error(dash_conn, event, poller):
						dashboard_connections.remove(dash_conn)
					else:
						message = dash_conn.recv(2048).decode()
						response = handle_dashboard_message(message, device_list, job_handler)
						dash_conn.send(response.encode())

				device = device_from_identifier(fd)
				if device is not None:
					if handle_socket_error(device.soc_connection, event, poller):
						log.info("Device " + str(device.id) + " disconnected.")
						device.disconnect()
					elif not handle_device_message(device):
						#TODO: Decide what to do depending how handle_device_message fails
						socket_close(device.soc_connection, poller)
						device.disconnect() 

		for d in device_list:
			device_status = d.update_pending()
			
			if device_status == SmartHome_Device.STATUS_UNRESPONSIVE:
				log.info("Device " + str(d.id) + " unresponsive. Closing connection")

			elif device_status == SmartHome_Device.STATUS_ERROR:
				log.info("Device " + str(d.id) + " socket error handled. Closing connection")
			
			if device_status != SmartHome_Device.STATUS_OK:
				handle_socket_error(d.soc_connection, select.POLLHUP, poller)
				d.disconnect()

		job_handler.run_tasks()

def run():
	init_log_file("device-manager.log")

	try:
		main_loop()
	except KeyboardInterrupt:
		raise
	except:
		log.critical("Caught unhandled exception; device manager has crashed!", exc_info = True)
		send_email("Device manager has crashed! Check logs for details.", subject="EasyDen Critical Error")
		exit(1)