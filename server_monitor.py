import common, config

import time, urllib.request

# Pass in instance of common.Logger.
def check_external_ip(logger):
	ip_log = config.BASE_DIR + "status_files/external_ip.log" 
	try: 
		with open(ip_log, "r") as ext_ip: 
			ipv4_last = ext_ip.read().strip()
	except FileNotFoundError as e:
		#TODO: a second FileNotFound indicates bad path.
		with open(ip_log, "w") as ext_ip:
			ipv4_last = "dummy address"
			ext_ip.write(ipv4_last)
	except Exception as e:
		logger.add_report("ERROR: Could not read previous IPv4, " + str(e), True)
		return False

	try:
		ipv4_new = urllib.request.urlopen("http://whatismyip.akamai.com").read().decode("utf-8").strip()
	except Exception as e:
		logger.add_report("ERROR: Failed to retrieve external IPv4. Skipping IP check.", True)
		return False

	if ipv4_new != ipv4_last:
		try:
			with open(ip_log, "w") as ext_ip: 
				ext_ip.write(ipv4_new)
			logger.add_report("NOTICE: New external IP address: " + ipv4_new)
		except FileNotFoundError as e:
			logger.add_report("ERROR: Failed to log updated IP address; bad file path?", True)
			return False
		except Exception as e:
			logger.add_report("ERROR: Failed to log updated IP address." + str(e), True)
			return False
	return True

if __name__ == "__main__":
	status_log = common.Logger(config.BASE_DIR + config.LOG_FILE)
	while True:
		ip_check = check_external_ip(status_log)
		if config.DEBUG:
			print("Checking external IPv4 address...")
			if ip_check:
				print("SUCCESS: Address updated.")
			else:
				print("FAILURE: Could not update address.")

		#TODO: More functionality here.
			# Check system uptime.
			# Check running server processes
			# IPC from other server components

		recorded = status_log.record_events()
		if config.DEBUG:
			print("\nAll checks complete. Recording events...")
			if recorded:
				print("SUCCESS: Events logged/reported.")
			else:
				print("FAILURE: Check logs or email for information.")
		
#TODO: Quick and dirty delay:
		if config.DEBUG:
			print("\nNOTICE: Sleeping for 6h.")
		time.sleep(3600 * 6)

#	sys.exit(0)

