
class Irrigation_Attributes extends React.Component {
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
				<p>moisture 0: { attrs.moisture[0].value?.toFixed(1) + " %" }</p>
				<p>moisture 1: { attrs.moisture[1].value?.toFixed(1) + " %" }</p>
			</div>
		)
	}
}

class Irrigation_Schedules extends React.Component {
	constructor(props) {
		super(props);
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
			<p><span>Target moisture: &nbsp;
				<input type="text" onChange={ 
					(e) => { }
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