#!/bin/sh
sqlite3 easyden.db << EOF
CREATE TABLE devices(
	id INTEGER PRIMARY KEY,
	type INTEGER,
	name TEXT
);

CREATE TABLE schedules (
	id INTEGER PRIMARY KEY,
	data TEXT,
	device_id INTEGER NOT NULL,
	FOREIGN KEY (device_id) REFERENCES devices (id)
);

CREATE TABLE thermostat_data (
	ext_id INTEGER NOT NULL,
	temperature REAL,
	target_temperature REAL,
	device_enabled INTEGER,
	online_status INTEGER,
	timestamp INTEGER NOT NULL,
	UNIQUE (ext_id, timestamp)
)
EOF
