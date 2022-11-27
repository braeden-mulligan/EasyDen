
class Device_Info extends React.Component {
	constructor(props) {
		super(props);
	}

	render() {
		return (
		<div>
			<p>Device { this.props.id } reporting for duty</p>
			<p>Name: { this.props.name }</p>
			<p>net status: { this.props.online.toString() }</p>
		</div>
		)
	}
}

class Thermostat extends React.Component {
	constructor(props) {
		super(props);
		this.current_target = 0.0;
	}

	render() {
		let attrs = this.props.attributes;
		return (
			<div>
				<p>Device enabled: { attrs.enabled.value }</p>
				<p>Temperature: { attrs.temperature.value }</p>
				<p>Target temperature: { attrs.target_temperature.value }</p>

				<input type="text" onChange={ 
					(e) => { this.current_target = e.target.value; console.log(e); }
				} /> 
				<button className="set" onClick={
					() => this.props.update_attribute(null, attrs.target_temperature.register, this.current_target, null)
				} > Set </button>

				<p>Min cooldown time: { attrs.min_cooldown_time.value }</p>
				<p>Max heat time: { attrs.max_heat_time.value }</p>
				<p>Min cooldown time: { attrs.min_cooldown_time.value }</p>
				<p>Temperature correction: { attrs.temperature_correction.value }</p>
				<p>Threshold high: { attrs.threshold_high.value }</p>
				<p>Threshold low: { attrs.threshold_low.value }</p>
			</div>
		)
	}
}

class Device extends React.Component {
	constructor(props) {
		super(props);
	}

	render() {
		let device_attributes;

		if (this.props.device_type == "thermostat") {
			device_attributes = <Thermostat attributes={ this.props.attributes } update_attribute={ this.props.update_attribute } />
		} else if (this.props.device_type == "poweroutlet") {
			device_attributes = <p> Poweroutlet </p>
		} else {
			device_attributes = <p> Uknown device type </p>
		}

		return (
			<div>
				<Device_Info id={ this.props.id } name={ this.props.name } online={ this.props.online } />
				{ device_attributes }
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
			//console.log("Raw response:");
			//console.log(xhr.responseText);
			data = JSON.parse(xhr.responseText)
			data_handler(data)
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

	let query_string = "?register=" + register.toString(); 
	if (id) query_string += "&id=" + register.toString();

	let url = "http://" + SERVER_ADDR + "/device/" + type + "/command" + query_string;

	let request = build_request(processor);
	request.open("POST", url, true);
	request.send(data);
}

let device_panel_container = document.getElementById("device-panel");
const root = ReactDOM.createRoot(device_panel_container);
root.render(<Device_Panel device_type={ device_panel_container.getAttribute("device-type") } />);

