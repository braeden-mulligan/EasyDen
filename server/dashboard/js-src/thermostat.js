
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
						() => this.props.update_attribute(attrs.enabled.register, + !attrs.enabled.value)
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
		this.current_target = null;
		this.current_hour = null;
		this.current_minute = null;
	}

	render_schedule(obj) {
		return (
			<li key={ JSON.stringify(obj.id_tag) }>
				{ JSON.stringify(obj) }
			<button className="set" onClick={
					() => this.props.set_schedule(JSON.stringify(Object.assign({ "action": "delete" }, obj.id_tag)))
				} > Remove </button>
			</li>
		)
	}

	render() {
		let schedules = this.props.schedules.map((obj, i) => {
			return this.render_schedule(obj, i)
		})

		if (!schedules.length) {
			schedules = <p>None</p>;
		}

		return (
			<div>
			<b>Schedules</b>
			<ul>
				{ schedules }
			</ul>
			<br />
			<b>New Schedule</b>
			<p><span>Target temperature: &nbsp;
				<input type="text" onChange={ 
					(e) => { this.current_target = e.target.value; }
				} />
				<br />
				<span><input type="text" placeholder="Hour" onChange={ 
					(e) => { this.current_hour = e.target.value; }
				} /></span> 
				<span>:<input type="text" placeholder="Minute" onChange={ 
					(e) => { this.current_minute = e.target.value; }
				} /></span>  
				<button className="set" onClick={
					() => this.props.set_schedule(
			build_schedule(this.props.attributes.target_temperature.register, this.current_target, "create", true, {hour: this.current_hour, minute: this.current_minute}) 
					)
				} > Add </button>
			</span></p>	
			</div>	
		);
	}
}