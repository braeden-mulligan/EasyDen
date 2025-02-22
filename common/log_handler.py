import logging, os

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

log_formatter = logging.Formatter("[%(asctime)s; %(levelname)s @ %(filename)s:%(lineno)d] - %(message)s")

log_console_handler = logging.StreamHandler()
log_console_handler.setLevel(logging.DEBUG)
log_console_handler.setFormatter(log_formatter)

logger.addHandler(log_console_handler)

log_file_handler = None

def init_log_file(file_name):
	global log_file_handler

	log_dir = os.path.dirname(__file__) + "/../logs"

	if not os.path.exists(log_dir):
		os.makedirs(log_dir)
	
	log_file_handler = logging.FileHandler(log_dir + "/" + file_name)
	log_file_handler.setLevel(logging.WARNING)
	log_file_handler.setFormatter(log_formatter)
	logger.addHandler(log_file_handler)

def set_log_level_console(level):
	log_console_handler.setLevel(level)

def set_log_level_file(level):
	global log_file_handler
	log_file_handler.setLevel(level)