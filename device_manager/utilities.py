
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
		
def reg_val_to_hex(json_device_list):
	return

