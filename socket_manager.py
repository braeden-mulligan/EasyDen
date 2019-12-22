import common, config 

import selectors, socket, time, types

HOST = "127.0.0.1"
PORT = 1338

N_MODULES = 4
TIMEOUT_SELECT = 2

def server_accept(soc):
	c_soc, addr = soc.accept()
	c_soc.setblocking(False)
	data = types.SimpleNamespace(addr = addr, r_bytes = b"", w_bytes = b"")
	events = selectors.EVENT_READ | selectors.EVENT_WRITE
	sel.register(c_soc, events, data=data)

	return True

def client_chat(key, mask):
#read format: "smarthome module,data key,data value"
#timestamp and write data to db
	soc = key.fileobj
	data = key.data
	if mask & selectors.EVENT_READ:
		recv_data = soc.recv(256)
		if recv_data:
			data.w_bytes += recv_data
		else:
			print("Closing " + str(data.addr))
			sel.unregister(soc)
			soc.close()	
	if mask & selectors.EVENT_WRITE:
		if data.w_bytes:
			print("ECHO: " + str(data.w_bytes) + " to " + str(data.addr))
			sent = soc.send(b"Returning " + data.w_bytes)
			data.w_bytes = data.w_bytes[sent:]

	return True

#TODO:
#if socket drop count too high:
	#log or send email
	#send email
if __name__ == "__main__":

	status_log = common.Logger(config.BASE_DIR + config.MODULES_LOG_FILE)

	sel = selectors.DefaultSelector()
	s_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s_soc.bind((HOST, PORT))
	s_soc.listen(N_MODULES)
	s_soc.setblocking(False)
	
	sel.register(s_soc, selectors.EVENT_READ)


	connections = [s_soc]
	while True:
		events = sel.select()
		for key, mask in events:
			if key.data is None:
				server_accept(key.fileobj)
			else:
				client_chat(key, mask)
		
