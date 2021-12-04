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

	write_html() {
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
