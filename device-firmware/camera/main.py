import os, sys

main_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(main_path + "/../..")
sys.path.append(main_path + "/..")

from libraries.linux.messaging_framework import Messaging_Framework
from common.log_handler import logger, init_log_file

def main():
	messaging_framework = Messaging_Framework(logger = logger, reconnect_delay = 5)
	messaging_framework.run()

if __name__ == "__main__":
	init_log_file("camera-main.log")
	main()