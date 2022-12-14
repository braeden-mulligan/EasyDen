
class Device_Info extends React.Component {
	constructor(props) {
		super(props);
	}

	render() {
		return (
		<div>
			<p>Device { this.props.id } reporting for duty</p>
			<p>Name: { this.props.name }</p>
			<p>Online: { this.props.online.toString() }</p>
		</div>
		)
	}
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

class Device extends React.Component {
	constructor(props) {
		super(props);
	}

	render() {
		let device_attributes = <p> Uknown device type </p>
		let device_schedules = <p>No schedules</p>

		if (this.props.device_type == "thermostat") {
			device_attributes = <Thermostat_Attributes attributes={ this.props.attributes } update_attribute={ this.props.update_attribute } />
			device_schedules = <Thermostat_Schedules attributes={ this.props.attributes } schedules={ this.props.schedules } set_schedule={ this.props.set_schedule } />
		} else if (this.props.device_type == "poweroutlet") {
			device_attributes = <Poweroutlet_Attributes attributes={ this.props.attributes } update_attribute={ this.props.update_attribute } />
			device_schedules = <Poweroutlet_Schedules attributes={ this.props.attributes } schedules={ this.props.schedules } set_schedule={ this.props.set_schedule } />
		}

		return (
			<div>
				<Device_Info id={ this.props.id } name={ this.props.name } online={ this.props.online } />
				{ device_attributes }
				{ device_schedules }
			</div>
		);
	}
}

class Device_Panel extends React.Component {
	poll_active = null;
	poll_period = 20000;

	constructor(props) {
		console.log(props);
		super(props);
		this.state = {
			devices: [ ]
		}
	}

	process_devices(fetched_list) {
		console.log("Processing")
		console.log(fetched_list)

		if (!Array.isArray(fetched_list)) return;

		let devices_copy = this.state.devices.slice();

		for (let i = 0; i < fetched_list.length; ++i) {
			let existing_device_index = devices_copy.findIndex(d => d.id == fetched_list[i].id);
			
			if (existing_device_index == -1) {
				devices_copy.push(fetched_list[i]);
			} else {
				devices_copy[existing_device_index] = fetched_list[i];
			}
		}

		this.setState({
			devices: devices_copy
		});
	}

	render_device(obj) {
		return (
			<li key={ obj.id }>
				<Device id={ obj.id } name={ obj.name } online={ obj.online } device_type= { this.props.device_type }
				  attributes={ obj.attributes } schedules={ obj.schedules }
				  update_attribute={ (register, data) => update_attribute(this.props.device_type, register, data, this.process_devices.bind(this), obj.id) }
				  set_schedule={ (data) => set_schedule(this.props.device_type, data, this.process_devices.bind(this), obj.id) } />
			</li>
		)
	}

	render() {
		let rendered_devices = this.state.devices.map((obj) => {
			return this.render_device(obj)
		})

		return (
			<div className="device-panel">
				<ul>
					{ rendered_devices }
				</ul>
			</div>
		)
	}

	start_poll(now = true) {
		console.log("start poll")
		if (this.poll_active) return;

		if (now) fetch_devices(this.props.device_type, this.process_devices.bind(this));

		this.poll_active = setInterval(function() {
			fetch_devices(this.props.device_type, this.process_devices.bind(this));
		}.bind(this), this.poll_period);
	}

	stop_poll = function() {
		if (this.poll_active) clearInterval(this.poll_active);
		this.poll_active = null;
	}

	componentDidMount() {
		this.start_poll();
	}

	componentWillUnmount() {
		this.stop_poll();
	} 
}

function build_request(data_handler) {
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
			data = JSON.parse(xhr.responseText);
			data_handler(data);
		}
	}

	return xhr;
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
		data: data
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
