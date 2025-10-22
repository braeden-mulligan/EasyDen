#!/bin/sh

sqlite3 easyden.db << EOF
CREATE TABLE if NOT EXISTS users (
	id INTEGER PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	email TEXT,
	password_hash TEXT NOT NULL
);

CREATE TABLE if NOT EXISTS devices (
	id INTEGER PRIMARY KEY,
	type INTEGER,
	name TEXT
);

CREATE TABLE if NOT EXISTS schedules (
	id INTEGER PRIMARY KEY,
	data TEXT,
	device_id INTEGER NOT NULL,
	FOREIGN KEY (device_id) REFERENCES devices (id)
);

CREATE TABLE if NOT EXISTS thermostat_data (
	device_id INTEGER NOT NULL,
	temperature REAL,
	target_temperature REAL,
	device_enabled INTEGER,
	online_status INTEGER,
	timestamp INTEGER NOT NULL,
	UNIQUE (device_id, timestamp)
)
EOF
