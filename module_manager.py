import config
import json, select, socket, sys, time, os

class SH_Device:
	CMD_NUL = 0
	CMD_GET = 1
	CMD_SET = 2
	CMD_RSP = 3
	CMD_PSH = 4
	CMD_IDY = 5
	CMD_DAT = 5

	def __init__(self, socket_connection = None):
		self.device_type = 0
		self.device_id = 0
		self.online_status = False 

#TODO: remove assigned debug value
		self.device_attrs = {6: -1} #(reg, val)

		self.msg_timeout = 2
		self.msg_retries = 1

		self.soc_connection = None
		self.soc_fd = None
		self.msg_seq = 1

# List of triples (message_string, timeout, retry_count) 
		self.pending_response = []

		self.connect(socket_connection)

	def get_json_obj(self):
		device_obj = {}
		device_obj["device_type"] = self.device_type
		device_obj["device_id"] = self.device_id
		device_obj["online_status"] = self.online_status
		device_obj["registers"] = self.device_attrs
		return device_obj

	def update_pending(self):
		for entry in self.pending_response:
			if time.time() > entry["timeout"]:
				retries = entry["retries"]
				self.pending_response.remove(entry)
				if retries > 0:
					print("Message [" + entry["msg"] + "] deilvery failed, retrying...")
					self.device_send(0, 0, 0, self.msg_timeout, retries - 1, entry["msg"]) 
				else:
					print("Message [" + entry["msg"] + "] deilvery failed.")
					# confirm failure

#TODO: debug version
	def update_attributes(self, reg, val):
		self.device_attrs[reg] = val

#TODO: improve parsing
	def parse_message(self, message_str):
		words = [int(w, 16) for w in message_str.split(',')]

		prev_msg_cmd = None
		prev_words = None
		for entry in self.pending_response:
			prev_words = [int(w, 16) for w in entry["msg"].split(',')]
			if prev_words[0] == words[0]:
				self.pending_response.remove(entry)
				prev_msg_cmd = prev_words[1]

		if words[1] == SH_Device.CMD_RSP and prev_msg_cmd == SH_Device.CMD_GET:
			self.update_attributes(words[2], words[3])
		elif words[1] == SH_Device.CMD_RSP and prev_msg_cmd == SH_Device.CMD_SET: 
			self.update_attributes(prev_words[2], prev_words[3])
			#confirm success or failure to inform web app
#TODO 
			pass
		elif words[1] == SH_Device.CMD_IDY:
			self.device_type = words[2]
			self.device_id = words[3]
			return self.device_id

		return None

#TODO: introduce delays for ESP to process?
#TODO: use queue?
	def device_send(self, cmd, reg, val, timeout = None, retries = None, raw_msg = None):
		timeout = timeout or self.msg_timeout
		retries = retries or self.msg_retries

		if self.soc_connection is not None:
			msg = raw_msg or "{:04X},{:02X},{:02X},{:08X}".format(self.msg_seq, cmd, reg, val)
			print("Device send: [" + msg + "]")

			t = time.time() + timeout
			self.pending_response.append({"msg": msg, "timeout": t, "retries": retries})
			#try:
			#TODO: except close broken connections 
			self.soc_connection.send(msg.encode())

			if raw_msg is None:
#TODO: wrap msg_seq, limited to 16 bits
				self.msg_seq += 1
			return True 
		return False

	def device_recv(self):
		if self.soc_connection is not None:
			#try: except
			msg = self.soc_connection.recv(32).decode()
			print("Device recv: [" + msg + "]")
			return self.parse_message(msg)
		return None

	def disconnect(self):
		self.online_status = False
		self.soc_connection = None
		self.soc_fd = None
		return

	def connect(self, soc_conn):
		self.soc_connection = soc_conn
		if soc_conn is not None:
			self.soc_fd = self.soc_connection.fileno()
			self.online_status = True
		return 

def connection_init(dashboard = False):
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

def check_socket_error(event, soc, poll_obj):
	if event & select.POLLHUP or event & select.POLLERR:
		print("Unregister fd " + str(fd))
		poller.unregister(soc)
		soc.close()
		return True
	return False

incoming_device_messages = []
outgoing_device_messages = []

if __name__ == "__main__":
	poller = select.poll()

	dash_soc = connection_init(dashboard = True)
	device_soc = connection_init()

	device_list = []
	dashboard_connections = []

#TODO POLLOUT
	poll_opts = select.POLLIN | select.POLLERR | select.POLLHUP
	poller.register(dash_soc, poll_opts)
	poller.register(device_soc, poll_opts)

	while True:
		for d in device_list:
			if not d.device_id and len(d.pending_response) == 0:
				d.device_send(SH_Device.CMD_IDY, 0, 0)

		poll_result = poller.poll(config.POLL_TIMEOUT)

		for fd, event in poll_result:
			msg = None
			print("\nFD: " + str(fd) + " EVENT: " + str(event))

			if (fd == dash_soc.fileno()):
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

#TODO: check IDENTIFY messages for previous device obj, ie. broken connections
#  then remove duplicates
				device_list.append(SH_Device(conn))

			else:
				dash_conn = next((d for d in dashboard_connections if d.fileno() == fd), None)

				if dash_conn is not None:
					if not check_socket_error(event, dash_conn, poller):
						msg = dash_conn.recv(2048).decode()
						print("Dash message: [" + msg + "]")

#TODO: debugging stuff here
						if "fetch" in msg:
							json_obj_list = []
							for d in device_list:
								json_obj_list.append(d.get_json_obj())
							dash_conn.send(json.dumps(json_obj_list).encode())
						elif "debug get" in msg:
							d_id = int(msg.split(' ')[2])
							for d in device_list:
								if d.device_id == d_id:
									d.device_send(SH_Device.CMD_GET, 6, 0)
						elif "debug set" in msg:
							d_id = int(msg.split(' ')[2])
							val = int(msg.split(' ')[3])
							val = 0xFFFF if val else 0xFF00
							for d in device_list:
								if d.device_id == d_id:
									d.device_send(SH_Device.CMD_SET, 6, val)

					else:
						dashboard_connections.remove(dash_conn)

				for d in device_list:
					if fd == d.soc_fd:
						if not check_socket_error(event, d.soc_connection, poller):
#TODO Fix this nested crap
							check_duplicate = d.device_recv()
							if check_duplicate:
								for dd in device_list:
									if check_duplicate == d.device_id and dd is not d:
										device_list.remove(dd)
						else:
							d.disconnect()

		for d in device_list:
			d.update_pending()

