import select, socket 

def socket_error(soc, event, poll_obj):
	if event & select.POLLHUP or event & select.POLLERR or event & select.POLLNVAL:
		print("Unregister fd " + str(soc.fileno))
		poll_obj.unregister(soc)
		soc.shutdown(socket.SHUT_RDWR)
		soc.close()
		return True
	return False

