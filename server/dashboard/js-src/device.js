const { useState, useEffect, useRef } = React;

function Device_Info({ id, name, online_status }) {
	return (
	<div>
		<p>Device { id } </p>
		<p>Name: { name }</p>
		<p>Online: { online_status?.toString() }</p>
	</div>
	)
}

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

function Schedule_Time_Selector({ on_update_schedule }) {
	const [days, set_days] = useState(Array(7).fill(false));

	function days_to_string(days) {
		weekdays = days[0] ? "mon" : "";
		weekdays += days[1] ? ((weekdays != "") ? "," : "") + "tue" : "";
		weekdays += days[2] ? ((weekdays != "") ? "," : "") + "wed" : "";
		weekdays += days[3] ? ((weekdays != "") ? "," : "") + "thu" : "";
		weekdays += days[4] ? ((weekdays != "") ? "," : "") + "fri" : "";
		weekdays += days[5] ? ((weekdays != "") ? "," : "") + "sat" : "";
		weekdays += days[6] ? ((weekdays != "") ? "," : "") + "sun" : "";
		return weekdays;
	}

	function handle_day_change(day_index, value) {
		new_days = days.slice(); 
		new_days[day_index] = value;
		on_update_schedule(null, days_to_string(new_days));
 		set_days(new_days);
	}

	return(<>
		<input type={"time"} onChange={ (e) => on_update_schedule(time = e.target.value, null) }/>
		<div>
			<input type={"checkbox"} id={"Mon"} onChange={ (e) => handle_day_change(0, e.target.checked) }/>
			<label>Mon</label>
		</div>
		<div>
			<input type={"checkbox"} id={"Tue"} onChange={ (e) => handle_day_change(1, e.target.checked) }/>
			<label>Tue</label>
		</div>
		<div>
			<input type={"checkbox"} id={"Wed"} onChange={ (e) => handle_day_change(2, e.target.checked) }/>
			<label>Wed</label>
		</div>
		<div>
			<input type={"checkbox"} id={"Thu"} onChange={ (e) => handle_day_change(3, e.target.checked) }/>
			<label>Thu</label>
		</div>
		<div>
			<input type={"checkbox"} id={"Fri"} onChange={ (e) => handle_day_change(4, e.target.checked) }/>
			<label>Fri</label>
		</div>
		<div>
			<input type={"checkbox"} id={"Sat"} onChange={ (e) => handle_day_change(5, e.target.checked) }/>
			<label>Sat</label>
		</div>
		<div>
			<input type={"checkbox"} id={"Sun"} onChange={ (e) => handle_day_change(6, e.target.checked) }/>
			<label>Sun</label>
		</div>
	</>)
}

function Device({ data, device_type, update_attribute, submit_schedule }) {
	let device_attributes = <p> Uknown device type </p>
	let device_schedules = <p>No schedules</p>

	if (device_type == "thermostat") {
		device_attributes = <Thermostat_Attributes attributes={ data.attributes } update_attribute={ update_attribute } />
		device_schedules = <Thermostat_Schedules attributes={ data.attributes } schedules={ data.schedules } submit_schedule={ submit_schedule } />
	} else if (device_type == "poweroutlet") {
		device_attributes = <Poweroutlet_Attributes attributes={ data.attributes } update_attribute={ update_attribute } />
		device_schedules = <Poweroutlet_Schedules attributes={ data.attributes } schedules={ data.schedules } submit_schedule={ submit_schedule } />
	} else if (device_type == "irrigation") {
		device_attributes = <Irrigation_Attributes attributes={ data.attributes } update_attribute={ update_attribute } />
		device_schedules = <Irrigation_Schedules attributes={ data.attributes } schedules={ data.schedules } submit_schedule={ submit_schedule } />
	}

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

		let existing_devices = devices.slice();

		for (let i = 0; i < fetched_list.length; ++i) {
			let new_device = true;

			for (let j = 0; j < existing_devices.length; ++j) {
				if (fetched_list[i].id == existing_devices[j].id) {
					if (!obj_equals(fetched_list[i], existing_devices[j])) existing_devices[j] = fetched_list[i];
					new_device = false;
					break;
				}
			}

			if (new_device) existing_devices.push(fetched_list[i]);
		}

		if (!obj_equals(devices, existing_devices)) set_devices(existing_devices);

	}

	useEffect(() => {
		fetch_devices(device_type, process_devices);
	}, [])

	useEffect(() => {
		const poll_timer = setInterval(function() {
			fetch_devices(device_type, process_devices);
		}, poll_period);

		return () => clearInterval(poll_timer);
	}, [devices])

	function render_device(obj) {
		return (
			<li key={ obj.id }>
				<Device data={ obj } device_type={ device_type }
				  update_attribute={ (register, data) => update_attribute(device_type, register, data, process_devices, obj.id) }
				  submit_schedule={ (schedule_data) => submit_schedule(device_type, schedule_data, process_devices, obj.id) }
 				/>
			</li>
		)
	}

	let rendered_devices = devices.map((obj) => {
	 	return render_device(obj)
	})

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
	if (ENVIRONMENT == "development") url = url.replace("/device/", "/debug/");

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
	if (ENVIRONMENT == "development") url = url.replace("/device/", "/debug/");

	let request = build_request(response_processor);
	request.open("PUT", url, true);
	request.send(payload);
}

function submit_schedule(type, data, response_processor, id = null) {
//console.log("set schedule" + data); return;
	let url = "http://" + SERVER_ADDR + "/device/" + type + "/schedule" + (id ? "?id=" + id.toString() : "");
	if (ENVIRONMENT == "development") url = url.replace("/device/", "/debug/");

	let request = build_request(response_processor);
	request.open("POST", url, true);
	request.send(data);
}

let device_panel_container = document.getElementById("device-panel");
const root = ReactDOM.createRoot(device_panel_container);
root.render(<Device_Panel device_type={ device_panel_container.getAttribute("device-type") } />);
