class Poweroutlet extends SH_Device {
	static class_label_socket_list = "poweroutlet-attr-socket-list";
	static class_label_socket_item = "poweroutlet-attr-socket-item";
	static class_label_socket_state = "poweroutlet-attr-socket-state";

	constructor(id, name, online, socket_count = 0, socket_states = []) {
		super(SH_Device.SH_TYPE_POWEROUTLET, id, name, online);
		this.socket_count = socket_count;
		this.socket_states = socket_states.slice();
	}

	copy() {
		var copy_states = this.socket_states.slice();
		return new Poweroutlet(this.id, this.name, this.online, this.socket_count, copy_states);
	}

	differ(sh_device) {
		if (this.type != sh_device.type) return undefined;

		if (super.differ(sh_device)) return true;

		for (var i = 0; i < this.socket_states.length; ++i) {
			if (this.socket_states[i] != sh_device.socket_states[i]) return true;
		}

		return false;
	}

	write_html(loading_flag = null) {
		var device_elem = super.write_html(loading_flag);

		var existing_elem = document.getElementById("device-" + this.id.toString());

		if (existing_elem != null) {
			// Update all attributes that are mutable.
			var socket_list;

			for (var i = 0; i < device_elem.children.length; ++i) {
				var attr = device_elem.children[i];
				if (attr.className == Poweroutlet.class_label_socket_list) socket_list = attr;
			}

			//each item should have a button and a state value
			for (var i = 0; i < socket_list.children.length; ++i) {
				var socket_item = socket_list.children[i];
				for (var j = 0; j < socket_item.children.length; ++j) {
					if (socket_item.children[j].className == Poweroutlet.class_label_socket_state) {
						socket_item.children[j].innerHTML = "Socket " + i + ": " + (this.socket_states[i] ? "ON" : "OFF");
					}
				}
			}

			return null;
		}

		var outlet_list = document.createElement("ul");
		outlet_list.setAttribute("class", Poweroutlet.class_label_socket_list);
		for (var i = 0; i < this.socket_states.length; ++i) {
			var entry = document.createElement("li");
			entry.setAttribute("class", Poweroutlet.class_label_socket_item);

			var outlet_state = document.createElement("p");
			outlet_state.setAttribute("class", Poweroutlet.class_label_socket_state);
			outlet_state.innerHTML = "Socket " + i + ": " + (this.socket_states[i] ? "ON" : "OFF");

			var toggle_button =  document.createElement("button");
			toggle_button.innerHTML = "Toggle";
			toggle_button.device_id = this.id;
			toggle_button.socket_index = i;
			toggle_button.addEventListener('click', toggle_action, false);

			entry.append(outlet_state);
			entry.append(toggle_button);

			outlet_list.append(entry);
		}

		device_elem.append(outlet_list);

//console.log(device_elem);
		return device_elem;
	}
}

class Poweroutlet_Tracker extends Data_Tracker {
	constructor() {
		super(SH_Device.SH_TYPE_POWEROUTLET);
	}

	request_response_processor = function(device_json, tracker, device_id) {
		for (var i = 0; i < device_json.length; ++i) {
			var d = device_json[i];
			if (d.id == device_id) {
				var entry = tracker.device_entry(device_id);
				if (entry) {
					tracker.devices_updated[entry.index] = new Poweroutlet(d.id, d.name, d.online, d.socket_states.length, d.socket_states);
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

		for (var i = 0; i < device_json.length; ++i) {
			var d = device_json[i];

			var poweroutlet = new Poweroutlet(d.id, d.name, d.online, d.socket_states.length, d.socket_states);
			var entry = tracker.device_entry(d.id);

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
	outlet_data = tracker.device_entry(evt.target.device_id).device.socket_states.slice();
	outlet_data[evt.target.socket_index] = +(!outlet_data[evt.target.socket_index]);
	send_command(evt.target.device_id, outlet_data, "poweroutlet");
	tracker.submit_tracking(evt.target.device_id);
}

// Main ----

tracker.start_global_poll(true);
