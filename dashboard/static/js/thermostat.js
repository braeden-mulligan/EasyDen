class Thermostat extends SH_Device {
	static class_label_temperature = "thermostat-attr-temperature";
	static class_label_humidity = "thermostat-attr-humidity";

	constructor(id, name, online, attributes = {}) { 
		super(SH_Device.SH_TYPE_THERMOSTAT, id, name, online);
		this.temperature = attributes?.temperature;
		this.humidity = attributes?.humidity;
		this.target_temperature = attributes?.target_temperature;
	}

	copy() {
		let attributes = {
			temperature: deep_copy(this.temperature),
			humidity: deep_copy(this.humidity),
			target_temperature: deep_copy(this.target_temperature)
		}
		return new Thermostat(this.id, this.name, this.online, attributes);
	}

	differ(sh_device) {
		if (this.type != sh_device.type) return undefined;

		if (super.differ(sh_device)) return true;

		if (this.temperature?.value != sh_device.temperature?.value) return true;
		if (this.humidity?.value != sh_device.humidity?.value) return true;

		return false;
	}

	write_html(loading_flag = null) {
		let device_elem = super.write_html(loading_flag);

		let existing_elem = document.getElementById("device-" + this.id.toString());

		if (existing_elem != null) {
			// Update all attributes that are mutable.
			for (let i = 0; i < device_elem.children.length; ++i) {
				let attr = device_elem.children[i];
				if (attr.className == Thermostat.class_label_temperature) {
					attr.innerHTML = "Temperature: " + this.temperature.value.toFixed(1) + " °C";

				} else if (attr.className == Thermostat.class_label_humidity) {
					if (!this.humidity.value) this.humidity.value = -0.69;
					attr.innerHTML = "Humidity: " + (this.humidity.value).toFixed(1) + " %";

				} else if (attr.className == "thermostat-attr-target-temperature") {
					attr.innerHTML = "Target temperature: " + this.target_temperature.value.toFixed(1) + " °C";
				}
			}

			return;
		}

		let temp = document.createElement("p");
		temp.setAttribute("class", Thermostat.class_label_temperature);
		temp.innerHTML = "Temperature: " + this.temperature.value.toFixed(1) + " °C";

		let hum = document.createElement("p");
		hum.setAttribute("class", Thermostat.class_label_humidity);
		if (!this.humidity?.value) this.humidity.value = -0.69;
		hum.innerHTML = "Humidity: " + (this.humidity.value).toFixed(1) + " %";

		//let target_temperature_form = document.createElement("form");
			let target_temperature = document.createElement("p");
			//target_temperature.setAttribute("method", "post");
			target_temperature.setAttribute("class", "thermostat-attr-target-temperature");
			target_temperature.innerHTML = "Target temperature: " + this.target_temperature.value.toFixed(1) + " °C";
			let target_input = document.createElement("input");
			target_input.setAttribute("type", "text");
			target_input.setAttribute("name", "target-temperature");
			target_input.setAttribute("id", "target-temperature-" + this.id);
			let target_submit =  document.createElement("button");
			target_submit.device_id = this.id;
			target_submit.innerHTML = "Set";
			target_submit.addEventListener('click', set_target_temperature, false);

		device_elem.append(temp);
		device_elem.append(hum);
		//device_elem.append(target_temperature_form);

		device_elem.append(target_temperature);
		device_elem.append(target_input);
		device_elem.append(target_submit);
		

		return device_elem;
	}
}

class Thermostat_Tracker extends Data_Tracker {
	constructor() {
		super(SH_Device.SH_TYPE_THERMOSTAT);
	}

	request_response_processor = function(device_json, tracker, device_id) {
		for (let i = 0; i < device_json.length; ++i) {
			let d = device_json[i];
			if (d.id == device_id) {
				let entry = tracker.device_entry(device_id);
				if (entry) {
					tracker.devices_updated[entry.index] = new Thermostat(d.id, d.name, d.online, d.attributes);
				} else {
					alert("Error: device mismatch. Contact Brad.");
				}
			}
		}
	}

	global_poll_response_processor = function(device_json, tracker) {
		if (!tracker.global_poll_active) return; 

		for (let i = 0; i < device_json.length; ++i) {
			let d = device_json[i];

			let thermostat = new Thermostat(d.id, d.name, d.online, d.attributes);
			let entry = tracker.device_entry(d.id);

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

function set_target_temperature(evt, value) {
	console.log("set device " + evt.target.device_id);
	let value_input = document.getElementById("target-temperature-" + evt.target.device_id).value;
	send_command(evt.target.device_id, value_input, "thermostat");
	tracker.submit_tracking(evt.target.device_id, "target_temperature");
}
tracker = new Thermostat_Tracker();

// Main ----

tracker.start_global_poll(true);
