from device_manager import config

import json, sqlite3


def load_devices(entry_processor):
	conn = sqlite3.connect(config.DATABASE_PATH)
	rows = conn.execute("select * from devices").fetchall()
	for row in rows:
		entry_processor(row)
	
	conn.close()

def add_device(device):
	conn = sqlite3.connect(config.DATABASE_PATH)
	query = "insert into devices(id, type, name) values({}, {}, \"{}\")".format(device.device_id, device.device_type, device.name)
	try:
		conn.cursor().execute(query)
	except sqlite3.IntegrityError:
		pass
	conn.commit()
	conn.close()

def update_device(device):
	#conn = sqlite3.connect(config.DATABASE_PATH)
	# select from devices where id == device.device_id
	# ... d.name ...
	return 

def remove_device():
	pass


def update_schedule(id, data):
	pass

def remove_schedule(id):
	conn = sqlite3.connect(config.DATABASE_PATH)
	conn.cursor().execute("delete from schedules where id={}".format(id))
	conn.commit()
	conn.close()

def add_schedule(schedule_obj):
	schedule_data = schedule_obj.get_data()
	schedule_data.pop("id", None)
	query = "insert into schedules(data, device_id) values(?, {})".format(schedule_obj.device.device_id)
	conn = sqlite3.connect(config.DATABASE_PATH)
	cursor = conn.cursor()
	cursor.execute(query, (json.dumps(schedule_data),))
	conn.commit()
	conn.close()
	return cursor.lastrowid

def load_schedules(device_list, entry_processor):
	device_ids = [d.device_id for d in device_list]
	query = "select * from schedules where device_id in ({ids})".format(ids = ','.join(['?'] * len(device_ids)))
	conn = sqlite3.connect(config.DATABASE_PATH)
	rows = conn.cursor().execute(query, device_ids)
	#row = (schedule id, data, device_id)
	for row in rows:
		entry_processor(row)

	conn.close()
