import json

def thermostat_fetch():
	fake_thermostats = [
    {
        "id": 13,
        "name": "Default Name",
        "online": True,
        "schedules": [
            {
                "id": 10,
                "recurring": True,
                "time": {
                    "hour": "20",
                    "minute": "00",
                    "days": ""
                },
                "pause": 0,
                "attribute": "target_temperature",
                "value": 17.0
            },
            {
                "id": 13,
                "recurring": True,
                "time": {
                    "hour": "08",
                    "minute": "30",
                    "days": "tue,wed,thu,fri"
                },
                "pause": 0,
                "attribute": "target_temperature",
                "value": 21.5
            },
            {
                "id": 14,
                "recurring": True,
                "time": {
                    "hour": "10",
                    "minute": "00",
                    "days": "mon,sat,sun"
                },
                "pause": 0,
                "attribute": "target_temperature",
                "value": 21.5
            }
        ],
        "attributes": {
            "enabled": {
                "value": 1,
                "register": "6"
            },
            "temperature": {
                "value": 21.762500762939453,
                "register": "128"
            },
            "target_temperature": {
                "value": 17.0,
                "register": "129"
            },
            "humidity": {
                "value": None
            },
            "threshold_high": {
                "value": 0.5,
                "register": "130"
            },
            "threshold_low": {
                "value": 0.5,
                "register": "131"
            },
            "temperature_correction": {
                "value": -0.30000001192092896,
                "register": "135"
            },
            "max_heat_time": {
                "value": 5400,
                "register": "132"
            },
            "min_cooldown_time": {
                "value": 300,
                "register": "133"
            }
        }
    }
	]

	fake_thermostats.append({
        "id": 14,
        "name": "Test thermostat 2",
        "online": True,
        "schedules": fake_thermostats[0]["schedules"],
        "attributes": fake_thermostats[0]["attributes"]
	})

	fake_thermostats.append({
        "id": 15,
        "name": "Test thermostat 3",
        "online": False,
		"schedules": fake_thermostats[0]["schedules"],
        "attributes": fake_thermostats[0]["attributes"]
	})

	return json.dumps(fake_thermostats)

def poweroutlet_fetch():
	fake_poweroutlets = [
    {
        "id": 11,
        "name": "Default Name",
        "online": True,
        "schedules": [
            {
                "id": 9,
                "recurring": True,
                "time": {
                    "hour": "17",
                    "minute": "50",
                    "days": "mon"
                },
                "pause": 0,
                "attribute": "socket_states",
                "value": [
                    1,
                    1,
                    1,
                    1
                ]
            }
        ],
        "attributes": {
            "enabled": {
                "value": 1,
                "register": "6"
            },
            "socket_count": {
                "value": 4,
                "register": "129"
            },
            "socket_states": {
                "value": [
                    0,
                    0,
                    0,
                    0
                ],
                "register": "128"
            }
        }
    },
    {
        "id": 12,
        "name": "Default Name",
        "online": True,
        "schedules": [],
        "attributes": {
            "enabled": {
                "value": 1,
                "register": "6"
            },
            "socket_count": {
                "value": 1,
                "register": "129"
            },
            "socket_states": {
                "value": [
                    0
                ],
                "register": "128"
            }
        }
    }
	]

	return json.dumps(fake_poweroutlets)