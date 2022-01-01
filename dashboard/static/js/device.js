class SH_Device {
	static SH_TYPE_NULL = 0;
	static SH_TYPE_RESERVED_1 = 1;
	static SH_TYPE_RESERVED_2 = 2;
	static SH_TYPE_RESERVED_3 = 3;
	static SH_TYPE_RESERVED_4 = 4;
	static SH_TYPE_RESERVED_5 = 5;
	static SH_TYPE_IRRIGATION = 6;
	static SH_TYPE_POWEROUTLET = 7;
	static SH_TYPE_THERMOSTAT = 8;
	static SH_TYPE_CAMERA = 9;

	static elem_tag_id = "div";
	static elem_tag_name = "div";
	static elem_tag_online = "div";
		
	static class_label_id = "sh-device-attr-id";
	static class_label_name = "sh-device-attr-name";
	static class_label_online = "sh-device-attr-online";

	constructor(type, id, name, online) {
		this.type = type;
		this.id = id;
		this.name = name;
		this.online = online;
		this.schedules = [];
	}

	copy() {
		//TODO: copy schedules.
		return new SH_Device(this.type, this.id, this.name, this.online);
	}

	differ(sh_device) {
		if (sh_device.type != this.type) return true;
		if (sh_device.id != this.id) return true;
		if (sh_device.name != this.name) return true;
		if (sh_device.online != this.online) return true;

		return false;
	}

	write_html(loading_flag = null) {
//TODO: pending update flag, states: inactive, loading, failed.

		var device_elem = document.createElement("div");
		device_elem.setAttribute("id", "device-" + this.id.toString());
		device_elem.setAttribute("class", "sh-device"); 

		var attr = document.createElement("div");
		attr.setAttribute("class", "sh-device-waiting-flag"); 
		attr.style.display = "none";
		device_elem.append(attr);

		attr = document.createElement(SH_Device.elem_tag_id);
		attr.innerHTML = this.id.toString();
		attr.setAttribute("class", SH_Device.class_label_id);
		device_elem.append(attr);

		attr = document.createElement(SH_Device.elem_tag_name);
		attr.innerHTML = this.name.toString();
		attr.setAttribute("class", SH_Device.class_label_name); 
		device_elem.append(attr);

		attr = document.createElement(SH_Device.elem_tag_online);
		attr.innerHTML = this.online.toString();
		attr.setAttribute("class", SH_Device.class_label_online); 
		device_elem.append(attr);

		return device_elem;
	}
}

class Data_Tracker {
	global_poll_period = 30000;
	fast_poll_timeout = 5000;
	fast_poll_interval = 410;

	global_poll_active = null;

	device_type = SH_Device.SH_TYPE_NULL;

// These should mirror each other
	devices = [];
	devices_updated = [];

	pending_requests = [];
	pending_request_obj = {
		//device_id
		//timeout_handle
		//interval_handle
	};

	constructor(device_type) {
		this.device_type = device_type;
		//this.start_global_poll();
	}

	device_entry = function(seek_id, list = this.devices) {
		for (var i = 0; i < list.length; ++i) {
			if (list[i].id == seek_id) return {device: list[i], index: i};
		}
		return null;
	}

	device_add = function(device) {
		for (var i = 0; i < this.devices.length; ++i) {
			//console.log(device.id + " : " + this.devices[i].id);
			if (device.id == this.devices[i].id) return false;
		}
		
		this.devices.push(device);
		this.devices_updated.push(device.copy());
		return true;
	}

	device_remove = function(device) {
		for (var i = 0; i < this.devices.length; ++i) {
			if (device.id == this.devces[i]) { 
				if (device.id != this.devices_updated[i]) {
					console.log("device_remove error: arrays not associated");
					return false;
				}

				this.devices.splice(i, 1);
				this.devices_updated.splice(i, 1);
				return true;
			}
		}

		return false;
	}

	request_response_processor = function(device_json, tracker, device_id) {
		console.log("Override this with device-specific response_processor.");
	}

	global_poll_response_processor = function(device_json, tracker) {
		console.log("Override this with device-specific response_processor.");
	}

	start_global_poll = function(now = true) {//, period = Data_Tracker.GLOBAL_POLL_PERIOD) {
		if (this.global_poll_active) return;

		if (now) fetch_devices(this, 0, this.device_type, false);

		this.global_poll_active = setInterval(function() {
			fetch_devices(this, 0, this.device_type, false);
		}.bind(this), this.global_poll_period);//period);
	}

	stop_global_poll = function() {
		if (this.global_poll_active) clearInterval(this.global_poll_active);
		this.global_poll_active = null;
	}

	request_timeout(device_id) {
		for (var i = 0; i < this.pending_requests.length; ++i) {
			if (this.pending_requests[i].device_id == device_id) {
				console.log("timeout on " + device_id.toString());
				clearInterval(this.pending_requests[i].interval_handle);
				clearTimeout(this.pending_requests[i].timeout_handle);
				this.pending_requests.splice(i, 1);

				var device = this.device_entry(device_id).device;
				device.write_html("error");
				
				this.start_global_poll(false);
			}
		}
	}
	
	request_check(seek_id /*, get vs set, notify_callback ?*/) {
		console.log("request_check: " + seek_id.toString());

		var current, after, index_pending;	

		for (var i = 0; i < this.pending_requests.length; ++i) {
			if (this.pending_requests[i].device_id == seek_id) {
				current = this.device_entry(seek_id, this.devices);
				after = this.device_entry(seek_id, this.devices_updated);
				index_pending = i;
			}
		}

		if (current == null || after == null) {
			console.log("request_check: device not found");
			return;
		}

		if (current.device.differ(after.device)) {
			console.log("Expected device update detected");
			clearInterval(this.pending_requests[index_pending].interval_handle);
			clearTimeout(this.pending_requests[index_pending].timeout_handle);
			this.pending_requests.splice(index_pending, 1);

			this.devices[current.index] = after.device.copy();
			this.devices[current.index].write_html("none");

			this.start_global_poll(false);

		} else {
			fetch_devices(this, seek_id, this.device_type, true);
		}
	}

	submit_tracking = function (id = 0 /*, notify_callback = null*/) {
		this.stop_global_poll();

		for (var i = 0; i < this.pending_requests.length; ++i) {
			if (this.pending_requests[i].device_id == device_id) return;
		}

		var device = this.device_entry(id).device;
		if (device == null) return;

		device.write_html("loading");

		var obj = this;
		fetch_devices(obj, id, this.device_type, true);

		var request = {
			device_id: id,

			timeout_handle: setTimeout(function() {
				this.request_timeout(id);
			}.bind(this), this.fast_poll_timeout),

			interval_handle: setInterval(function() {
				this.request_check(id);
			}.bind(this), this.fast_poll_interval)
		}

		this.pending_requests.push(request);
	}
}

function fetch_devices(tracker, id = 0, type = null, fast_poll = true) {
//TODO: if fast polling active just return?
	console.log("fetching devices via " + (fast_poll ? "fast poll" : "global poll"));

	var type_label;
	switch (type) {
		case SH_Device.SH_TYPE_POWEROUTLET: type_label = "poweroutlet"; break;
		case SH_Device.SH_TYPE_THERMOSTAT: type_label = "thermostat"; break;
		default: return;
	}

	var url = "http://" + SERVER_ADDR + "/device/" + type_label + "/refresh" + (id ? "?id=" + id.toString() : "");

	try {
		var xhr = new XMLHttpRequest();
	} catch (e) {
		alert("Something went wrong!");
		return false;
	}

	xhr.onreadystatechange = function() {
		if (xhr.readyState == XMLHttpRequest.DONE) {
			console.log("Raw response:");
			console.log(xhr.responseText);
			fetch_json = JSON.parse(xhr.responseText);
			if (fast_poll) {
				tracker.request_response_processor(fetch_json, tracker, id);
			} else {
				tracker.global_poll_response_processor(fetch_json, tracker);
			}
		}
	}

	xhr.open("GET", url, true);
	xhr.send();
}

function send_command(id, command, device_url_snippet) {
	console.log("Sending...");
	console.log(command);
	var url = "http://" + SERVER_ADDR + "/device/"+ device_url_snippet + "/command?id=" + id;

	try {
		var xhr = new XMLHttpRequest();
	} catch (e) {
		alert("Something went wrong!");
		return false;
	}

	xhr.onreadystatechange = function() {
		if (xhr.readyState == XMLHttpRequest.DONE) {
			console.log(xhr.responseText);
		}
	}

	xhr.open("POST", url, true);
	xhr.send(command);
}
