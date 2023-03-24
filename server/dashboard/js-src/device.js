const { useState, useEffect } = React;

function Device_Info({ id, name, online_status }) {
	return (
	<div>
		<p>Device { id } </p>
		<p>Name: { name }</p>
		<p>Online: { online_status?.toString() }</p>
	</div>
	)
}

/*
function Mutable_Attribute(props) {
	let current_target;

	return (
		<p><span>{ props.description }: { props.attribute.value } &nbsp;
			<input type="text" onChange={ 
				(e) => { current_target = e.target.value; }
			} /> 
			<button className="set" onClick={
				() => props.update_attribute(props.attribute.register, current_target)
			} > Set </button>
		</span></p>
	);
}
*/

function Device({ data, update_attribute, set_schedule }) {
	let device_attributes = <p> Uknown device type </p>
	let device_schedules = <p>No schedules</p>

	/*if (data.device_type == "thermostat") {
		device_attributes = <Thermostat_Attributes attributes={ data.attributes } update_attribute={ data.update_attribute } />
		device_schedules = <Thermostat_Schedules attributes={ data.attributes } schedules={ data.schedules } set_schedule={ data.set_schedule } />
	} else if (data.device_type == "poweroutlet") {
		device_attributes = <Poweroutlet_Attributes attributes={ data.attributes } update_attribute={ data.update_attribute } />
		device_schedules = <Poweroutlet_Schedules attributes={ data.attributes } schedules={ data.schedules } set_schedule={ data.set_schedule } />
	} else if (data.device_type == "irrigation") {
		device_attributes = <Irrigation_Attributes attributes={ data.attributes } update_attribute={ data.update_attribute } />
		device_schedules = <Irrigation_Schedules attributes={ data.attributes } schedules={ data.schedules } set_schedule={ data.set_schedule } />
	}*/

	return (
	<div>
		<Device_Info id={ data.id } name={ data.name } online_status={ data.online } />
			{ device_attributes }
			{ device_schedules }
	</div>
	)
}

function Device_Panel({ device_type }) {
	const poll_period = 20000;
	const [devices, set_devices] = useState([])

	function process_devices(fetched_list) {
		if (!Array.isArray(fetched_list)) return;
		if (!obj_equals(devices, fetched_list)) set_devices(fetched_list)
	}

	useEffect(() => {
		fetch_devices(device_type, process_devices.bind(this));
	}, [])

	useEffect(() => {
		const poll_timer = setInterval(function() {
			fetch_devices(device_type, process_devices.bind(this));
		}, poll_period);

		return () => clearInterval(poll_timer);
	}, [devices])

	function render_device(obj) {
		return (
			<li key={ obj.id }>
				<Device data={ obj } 
				  update_attribute={ (register, data) => update_attribute(device_type, register, data, process_devices, obj.id) }
				  set_schedule={ (schedule_data) => set_schedule(device_type, schedule_data, process_devices, obj.id) }
 				/>
			</li>
		)
	}

	let rendered_devices = devices.map((obj) => {
	 	return render_device(obj)
	})

	console.log("RENDERING")
	return (
	<div className="device-panel">
		<ul>
			{ rendered_devices }
		</ul>
	</div>
	)
}

function fetch_devices(type, response_processor, id = null) {
	let url = "http://" + SERVER_ADDR + "/device/" + type + "/refresh" + (id ? "?id=" + id.toString() : "");

	let request = build_request(response_processor);
	request.open("GET", url, true);
	request.send();
}

function update_attribute(type, register, data, response_processor, id = null) {
	console.log("Send reg: " + register.toString() + " data: " + data.toString() + " for id:" + id.toString()) 

	let payload = JSON.stringify({
		register: register,
		attribute_data: data
	})

	let url = "http://" + SERVER_ADDR + "/device/" + type + "/command" + (id ? ("?id=" + id.toString()) : "");

	let request = build_request(response_processor);
	request.open("PUT", url, true);
	request.send(payload);
}

function set_schedule(type, data, response_processor, id = null) {
//console.log("set schedule" + data); return;
	let url = "http://" + SERVER_ADDR + "/device/" + type + "/schedule" + (id ? "?id=" + id.toString() : "");

	let request = build_request(response_processor);
	request.open("POST", url, true);
	request.send(data);
}

let device_panel_container = document.getElementById("device-panel");
const root = ReactDOM.createRoot(device_panel_container);
root.render(<Device_Panel device_type={ device_panel_container.getAttribute("device-type") } />);
