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

	schedules = [];

	constructor(type, id, name, online) {
		this.type = type;
		this.id = id;
		this.name = name;
		this.online = online;
	}

	copy() {
		return new SH_Device(this.type, this.id, this.name, this.online);
	}

	differ(sh_device) {
		if (sh_device.type != this.type) return true;
		if (sh_device.id != this.id) return true;
		if (sh_device.name != this.name) return true;
		if (sh_device.online != this.online) return true;

		return false;
	}

	write_html() {
//TODO: pending update flag, states: inactive, loading, failed.

		var device_elem = document.createElement("div");
		device_elem.setAttribute("id", "device-" + this.id.toString());
		device_elem.setAttribute("class", "sh-device"); 

		var attr = document.createElement(SH_Device.elem_tag_id);
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
	global_poll = null;

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
		//if (response_processor) this.ajax_response_processor = response_processor;
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
			console.log(device.id + " : " +this.devices[i].id);
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

	request_response_processor = function(device_json, tracking_object) {
		console.log(device_json);
	}

	global_poll_response_processor = function(device_json, tracking_object) {
		console.log(device_json);
		for (var i = 0; i < tracking_object.devices.length; ++i) {
			if (tracking_object.devices[i].differ(tracking_object.devices_updated[i])) {
				console.log("Global poll found diff");
				tracking_object.devices[i] = tracking_object.devices_updated[i].copy();
			}
		}
	}

	start_global_poll = function(now = true) {
		if (this.global_poll) return;

		var obj = this;
		if (now) fetch_devices(obj, false, 0, this.device_type);

		this.global_poll = setInterval(function() {
			fetch_devices(obj, false, 0, this.device_type);
		}.bind(this), 10000);
	}

	stop_global_poll = function() {
		if (this.global_poll) clearInterval(this.global_poll);
		this.global_poll = null;
	}

	request_timeout(device_id) {
		for (var i = 0; i < this.pending_requests.length; ++i) {
			if (this.pending_requests[i].device_id = device_id) {
				console.log("timeout on " + device_id.toString());
				clearInterval(this.pending_requests[i].interval_handle);
				clearTimeout(this.pending_requests[i].timeout_handle);
				this.pending_requests.splice(i, 1);
				//TODO: device.html_write pending flag failed 
				
				start_global_poll(false);
			}
		}
	}
	
	request_check(device_id /*, get vs set, notify_callback ?*/) {
		console.log("request_check: " + device_id.toString());

		for (var i = 0; i < this.pending_requests.length; ++i) {
			if (this.pending_requests[i].device_id = device_id) {
				var current = this.device_entry(device_id, this.devices);
				var after = this.device_entry(device_id, this.devices_updated);

				if (current == null || after == null) {
					console.log("request_check: device not found");
					return;
				}

				if (current.device.differ(after.device)) {
					console.log("Device update detected");
					clearInterval(this.pending_requests[i].interval_handle);
					clearTimeout(this.pending_requests[i].timeout_handle);
					this.pending_requests.splice(i, 1);

					//TODO: verify if copy is necessary
					this.devices[current.index] = after.device.copy();
					//TODO: set html pending flag inactive

					start_global_poll(false);
				}
			}
		}
	}

	submit_tracking = function (id = 0, notify_callback = null) {
		this.stop_global_poll();

		for (var i = 0; i < this.pending_requests.length; ++i) {
			if (this.pending_requests[i].device_id = device_id) return;
		}

		var device = this.device_entry(id).device;
		if (device == null) return;

		//TODO: device.write_html(pending_flag);

		var request = {
			device_id: id,

			timeout_handle: setTimeout(function() {
				this.request_timeout(id);
			}.bind(this), 5000),

			interval_handle: setInterval(function() {
				this.request_check(id);
			}.bind(this), 300)
		}

		this.pending_requests.push(request);
	}
}

function fetch_devices(tracking_object, fast_poll = true, id = 0, type = SH_Device.SH_TYPE_NULL) {
	console.log("fetching devices");

	var category = "type";
	var selector = type.toString();
	if (id) {
		category = "id";
		selector = id.toString();
	}

	var url = "http://" + server_addr + "/device/refresh?category=" + category + "&selector=" + selector;

	try {
		var xhr = new XMLHttpRequest();
	} catch (e) {
		alert("Something went wrong!");
		return false;
	}

	xhr.onreadystatechange = function() {
		if (xhr.readyState == XMLHttpRequest.DONE) {
			console.log(xhr.responseText);
			devices = JSON.parse(xhr.responseText);
			if (fast_poll) {
				tracking_object.request_response_processor(devices, tracking_object);
			} else {
				tracking_object.global_poll_response_processor(devices, tracking_object);
			}
		}
	}

	xhr.open("GET", url, true);
	xhr.send();
}
