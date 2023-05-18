#!/bin/sh
sqlite3 test.db << EOF
CREATE TABLE devices(
	id INTEGER PRIMARY KEY,
	type INTEGER,
	name TEXT);

CREATE TABLE schedules (
	id INTEGER PRIMARY KEY,
	data TEXT,
	device_id INTEGER NOT NULL,
	FOREIGN KEY (device_id) REFERENCES devices (id));
EOF
