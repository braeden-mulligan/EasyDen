import sys
sys.path.append("..")
from common import defines 

import json, sqlite3

def db_connection(operation):
	def inner(*args, **kwargs):
		conn = sqlite3.connect(defines.DATABASE_PATH)
		cursor = conn.cursor()
		result = operation(*args, **kwargs, db = cursor)
		conn.commit()
		conn.close()
		return result
	return inner

@db_connection
def load_devices(entry_processor, db = None):
	rows = db.execute("select * from devices").fetchall()
	for row in rows:
		entry_processor(row)

@db_connection
def add_device(device, db = None):
	query = "insert into devices(id, type, name) values({}, {}, \"{}\")".format(device.id, device.type, device.name)
	try:
		db.execute(query)
	except sqlite3.IntegrityError:
		pass

#TODO
@db_connection
def update_device_name(device, db = None):
	query = "update devices set name = \"{}\" where id = {}".format(device.name, device.id)
	db.execute(query)
	return 

@db_connection
def remove_device(db = None):
	pass


@db_connection
def update_schedule(id, data, db = None):
	pass

@db_connection
def remove_schedule(id, db = None):
	db.execute("delete from schedules where id={}".format(id))

@db_connection
def add_schedule(schedule, db = None):
	schedule_data = schedule.get_data()
	schedule_data.pop("id", None)
	query = "insert into schedules(data, device_id) values(?, {})".format(schedule.device.id)
	db.execute(query, (json.dumps(schedule_data),))
	return db.lastrowid

@db_connection
def load_schedules(device_list, entry_processor, db = None):
	device_ids = [d.id for d in device_list]
	query = "select * from schedules where device_id in ({ids})".format(ids = ','.join(['?'] * len(device_ids)))
	rows = db.execute(query, device_ids)
	#row = (schedule id, data, device_id)
	for row in rows:
		entry_processor(row)

@db_connection
def fetch_thermostat_data(device_id, date_start, date_end, db = None):
	pass

@db_connection
def store_thermostat_data(entries, db = None):
	for entry in entries:
		db.execute("insert into thermostat_data(ext_id, temperature, target_temperature, device_enabled, online_status, timestamp) values(?, ?, ?, ?, ? ,?)", entry)

