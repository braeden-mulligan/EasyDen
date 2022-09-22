class Thermostat extends SH_Device {
	static class_label_temperature = "thermostat-attr-temperature";
	static class_label_humidity = "thermostat-attr-humidity";

	constructor(id, name, online, temperature = {}, humidity = {}) {
		super(SH_Device.SH_TYPE_THERMOSTAT, id, name, online);
		this.temperature = temperature;
		this.humidity = humidity
	}

	copy() {
		let temperature = JSON.parse(JSON.stringify(this.temperature))
		let humidity = JSON.parse(JSON.stringify(this.humidity))
		return new Thermostat(this.id, this.name, this.online, temperature, humidity);
	}

	differ(sh_device) {
		if (this.type != sh_device.type) return undefined;

		if (super.differ(sh_device)) return true;

		if (this.temperature?.value != sh_device.temperature?.value) return true;
		if (this.humidity?.value != sh_device.humidity?.value) return true;

		return false;
	}

	write_html(loading_flag = null) {
		var device_elem = super.write_html(loading_flag);

		var existing_elem = document.getElementById("device-" + this.id.toString());

console.log(this.temperature)
		if (existing_elem != null) {
			// Update all attributes that are mutable.
			for (var i = 0; i < device_elem.children.length; ++i) {
				var attr = device_elem.children[i];
				if (attr.className == Thermostat.class_label_temperature) {
					attr.innerHTML = "Temperature: " + this.temperature.value.toFixed(1) + " °C";

				} else if (attr.className == Thermostat.class_label_humidity) {
					if (!this.humidity.value) this.humidity.value = -0.69;
					attr.innerHTML = "Humidity: " + (this.humidity.value * 100).toFixed(1) + " %";
				}
			}

			return;
		}

		var temp = document.createElement("p");
		temp.setAttribute("class", Thermostat.class_label_temperature);
		temp.innerHTML = "Temperature: " + this.temperature.value.toFixed(1) + " °C";

		var hum = document.createElement("p");
		hum.setAttribute("class", Thermostat.class_label_humidity);
		if (!this.humidity.value) this.humidity.value = -0.69;
		hum.innerHTML = "Humidity: " + (this.humidity.value * 100).toFixed(1) + " %";

		device_elem.append(temp);
		device_elem.append(hum);

		return device_elem;
	}
}

class Thermostat_Tracker extends Data_Tracker {
	constructor() {
		super(SH_Device.SH_TYPE_THERMOSTAT);
	}

	request_response_processor = function(device_json, tracker, device_id) {
		for (var i = 0; i < device_json.length; ++i) {
			var d = device_json[i];
			if (d.id == device_id) {
				var entry = tracker.device_entry(device_id);
				if (entry) {
					tracker.devices_updated[entry.index] = new Thermostat(d.id, d.name, d.online, d.temperature, d.humidity);
				} else {
					alert("Error: device mismatch. Contact Brad.");
				}
			}
		}
	}

	global_poll_response_processor = function(device_json, tracker) {
		if (!tracker.global_poll_active) return; 

		for (var i = 0; i < device_json.length; ++i) {
			var d = device_json[i];

			var thermostat = new Thermostat(d.id, d.name, d.online, d.temperature, d.humidity);
			var entry = tracker.device_entry(d.id);

			if (entry) {
				tracker.devices_updated[entry.index] = thermostat;

				if (tracker.devices[entry.index].differ(thermostat)) {
					console.log("Global poll found diff");
					tracker.devices_updated[entry.index].write_html();
				}
				tracker.devices[i] = tracker.devices_updated[i].copy();

			} else {
				console.log("Global poll found new device");
				append_device_node(thermostat.write_html());
				tracker.device_add(thermostat);
			}
		}
	}
}

tracker = new Thermostat_Tracker();

// Main ----

tracker.start_global_poll(true);
