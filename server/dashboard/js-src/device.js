
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
				() => props.update_attribute(null, props.attribute.register, current_target, null)
			} > Set </button>
		</span></p>
	);
}

class Poweroutlet_Attributes extends React.Component {
	constructor(props) {
		super(props);
	}

	render_socket_states() {
		let attrs = this.props.attributes;

		let rendered_sockets = attrs.socket_states.value.map((val, i) => {
			return(
				<li key={ i }>
					<span socket_id={i}>Socket {i}: {val ? "ON" : "OFF"} &nbsp; </span>
					<button className="set" onClick={
						() => {
							let socket_states = attrs.socket_states.value.slice();
							socket_states[i] = + !socket_states[i];
							this.props.update_attribute(null, attrs.socket_states.register, socket_states, null)
						}
					} > Toggle </button>
				</li>
			);
		});

		console.log(rendered_sockets)

		return rendered_sockets;
	}

	render() {
		let attrs = this.props.attributes;
		return (
			<div>
				<p>Device enabled: { attrs.enabled.value } &nbsp;
					<button className="set" onClick={
						() => this.props.update_attribute(null, attrs.enabled.register, + !attrs.enabled.value, null)
					} > Toggle </button>
				</p>
				<ul>
					{ this.render_socket_states() }
				</ul>
			</div>
		)
	}
}

class Thermostat_Attributes extends React.Component {
	constructor(props) {
		super(props);
	}

	render() {
		let attrs = this.props.attributes;
		return (
			<div>
				<p>Device enabled: { attrs.enabled.value } &nbsp;
					<button className="set" onClick={
						() => this.props.update_attribute(null, attrs.enabled.register, + !attrs.enabled.value, null)
					} > Toggle </button>
				</p>
				<p>Temperature: { attrs.temperature.value.toFixed(1) + " °C" }</p>
				<Mutable_Attribute description="Target Temperature" attribute={ attrs.target_temperature } update_attribute={ this.props.update_attribute } />
				<Mutable_Attribute description="Temperature correction" attribute={ attrs.temperature_correction } update_attribute={ this.props.update_attribute } />
				<Mutable_Attribute description="Threshold high" attribute={ attrs.threshold_high } update_attribute={ this.props.update_attribute } />
				<Mutable_Attribute description="Threshold low" attribute={ attrs.threshold_low } update_attribute={ this.props.update_attribute } />
				<Mutable_Attribute description="Max heat time" attribute={ attrs.max_heat_time } update_attribute={ this.props.update_attribute } />
				<Mutable_Attribute description="Min cooldown time" attribute={ attrs.min_cooldown_time } update_attribute={ this.props.update_attribute } />
			</div>
		)
	}
}

class Thermostat_Schedules extends React.Component {
	constructor(props) {
		super(props);
	}

	render() {
		return (
			<p>No schedules</p>
		);
	}
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
			device_schedules= <Thermostat_Schedules attributes={ this.props.attributes } />
		} else if (this.props.device_type == "poweroutlet") {
			device_attributes = <Poweroutlet_Attributes attributes={ this.props.attributes } update_attribute={ this.props.update_attribute } />
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
				<Device id={ obj.id } name={ obj.name } online={ obj.online } attributes={ obj.attributes } device_type= { this.props.device_type }
				  update_attribute={ (type, register, data, processor) => update_attribute(this.props.device_type, register, data, this.process_devices.bind(this), obj.id) } />
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

function fetch_devices(type, processor, id = null) {
	if (!type) {
		console.log("Failed to fetch, no type specified");
		return;
	}

	let url = "http://" + SERVER_ADDR + "/device/" + type + "/refresh" + (id ? "?id=" + id.toString() : "");

	let request = build_request(processor);
	request.open("GET", url, true);
	request.send();
}

function update_attribute(type, register, data, processor, id = null) {
	if (!type) {
		console.log("Failed to update attribute, no type specified");
		return;
	}

	console.log("Send reg: " + register.toString() + " data: " + data.toString() + " for id:" + id.toString()) 

	let query_string = "?register=" + register.toString(); 
	if (id) query_string += "&id=" + id.toString();

	console.log(query_string);

	let url = "http://" + SERVER_ADDR + "/device/" + type + "/command" + query_string;

	let request = build_request(processor);
	request.open("POST", url, true);
	request.send(data);
}

let device_panel_container = document.getElementById("device-panel");
const root = ReactDOM.createRoot(device_panel_container);
root.render(<Device_Panel device_type={ device_panel_container.getAttribute("device-type") } />);
