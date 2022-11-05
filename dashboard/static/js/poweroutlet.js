class Poweroutlet extends SH_Device {
	static class_label_socket_list = "poweroutlet-attr-socket-list";
	static class_label_socket_item = "poweroutlet-attr-socket-item";
	static class_label_socket_state = "poweroutlet-attr-socket-state";

	constructor(id, name, online, attributes = {}) {
		super(SH_Device.SH_TYPE_POWEROUTLET, id, name, online);
		this.socket_states = deep_copy(attributes?.socket_states);
		this.socket_count = attributes.socket_count || this.socket_states?.length;
	}

	copy() {
		let attributes = {
			socket_count: this.socket_count,
			socket_states: deep_copy(this.socket_states)
		}
		return new Poweroutlet(this.id, this.name, this.online, attributes);
	}

	differ(sh_device) {
		if (this.type != sh_device.type) return undefined;

		if (super.differ(sh_device)) return true;

		for (let i = 0; i < this.socket_states.value.length; ++i) {
			if (this.socket_states.value[i] != sh_device.socket_states.value[i]) return true;
		}

		return false;
	}

	write_html(loading_flag = null) {
		let device_elem = super.write_html(loading_flag);

		let existing_elem = document.getElementById("device-" + this.id.toString());

		if (existing_elem != null) {
			// Update all attributes that are mutable.
			let socket_list;

			for (let i = 0; i < device_elem.children.length; ++i) {
				let attr = device_elem.children[i];
				if (attr.className == Poweroutlet.class_label_socket_list) socket_list = attr;
			}

			//each item should have a button and a state value
			for (let i = 0; i < socket_list.children.length; ++i) {
				let socket_item = socket_list.children[i];
				for (let j = 0; j < socket_item.children.length; ++j) {
					if (socket_item.children[j].className == Poweroutlet.class_label_socket_state) {
						socket_item.children[j].innerHTML = "Socket " + i + ": " + (this.socket_states.value[i] ? "ON" : "OFF");
					}
				}
			}

			return null;
		}

		let outlet_list = document.createElement("ul");
		outlet_list.setAttribute("class", Poweroutlet.class_label_socket_list);
		for (let i = 0; i < this.socket_states.value.length; ++i) {
			let entry = document.createElement("li");
			entry.setAttribute("class", Poweroutlet.class_label_socket_item);

			let outlet_state = document.createElement("p");
			outlet_state.setAttribute("class", Poweroutlet.class_label_socket_state);
			outlet_state.innerHTML = "Socket " + i + ": " + (this.socket_states.value[i] ? "ON" : "OFF");

			let toggle_button =  document.createElement("button");
			toggle_button.innerHTML = "Toggle";
			toggle_button.device_id = this.id;
			toggle_button.socket_index = i;
			toggle_button.addEventListener('click', toggle_action, false);

			entry.append(outlet_state);
			entry.append(toggle_button);

			outlet_list.append(entry);
		}

		device_elem.append(outlet_list);

		return device_elem;
	}
}

class Poweroutlet_Tracker extends Data_Tracker {
	constructor() {
		super(SH_Device.SH_TYPE_POWEROUTLET);
	}

	request_response_processor = function(device_json, tracker, device_id) {
		for (let i = 0; i < device_json.length; ++i) {
			let d = device_json[i];
			if (d.id == device_id) {
				let entry = tracker.device_entry(device_id);
				if (entry) {
					tracker.devices_updated[entry.index] = new Poweroutlet(d.id, d.name, d.online, d.attributes);
				} else {
					alert("Error: device mismatch. Contact Brad.");
				}
			}
		}
	}

	global_poll_response_processor = function(device_json, tracker) {
		// Check in case active tracking was started between the originating request and this callback.
		//   We don't want the active tracking to miss an update.
		if (!tracker.global_poll_active) return; 

		for (let i = 0; i < device_json.length; ++i) {
			let d = device_json[i];

			let poweroutlet = new Poweroutlet(d.id, d.name, d.online, d.attributes);
			let entry = tracker.device_entry(d.id);

			if (entry) {
				tracker.devices_updated[entry.index] = poweroutlet;

				if (tracker.devices[entry.index].differ(poweroutlet)) {
					console.log("Global poll found diff");
					tracker.devices_updated[entry.index].write_html();
				}
				tracker.devices[i] = tracker.devices_updated[i].copy();

			} else {
				console.log("Global poll found new device");
				append_device_node(poweroutlet.write_html());
				tracker.device_add(poweroutlet);
			}
		}
	}
}

tracker = new Poweroutlet_Tracker();

//TODO: This is debug only
function toggle_action(evt) {
	outlet_data = tracker.device_entry(evt.target.device_id).device.socket_states.value.slice();
	outlet_data[evt.target.socket_index] = +(!outlet_data[evt.target.socket_index]);
	send_command(evt.target.device_id, outlet_data, "poweroutlet");
	tracker.submit_tracking(evt.target.device_id, "socket_states");
}

// Main ----

tracker.start_global_poll(true);
