import module_manager 

import socket 

def data_transaction(msg, timeout = 1.0):
	soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		soc.connect(module_manager.config.SERVER_INTERCONNECT)
	except ConnectionRefusedError as e:
		return "ERROR: " + str(e)
	except Exception as e:
		return "ERROR: " + str(e)
	
	soc.settimeout(timeout)

	soc.send(msg.encode())

	resp = ""
	try:
		resp = soc.recv(65536).decode()
		print("Dashboard got: " + resp)
	except Exception as e:
		resp = "ERROR: " + str(e)
		print(e)

	soc.shutdown(socket.SHUT_RDWR)
	soc.close()

	return resp
