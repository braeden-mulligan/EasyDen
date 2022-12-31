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
							this.props.update_attribute(attrs.socket_states.register, socket_states)
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
						() => this.props.update_attribute(attrs.enabled.register, + !attrs.enabled.value)
					} > Toggle </button>
				</p>
				<ul>
					{ this.render_socket_states() }
				</ul>
			</div>
		)
	}
}

//TODO: Dehackify this
class Poweroutlet_Schedules extends React.Component {
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
			<p><span>Socket values&nbsp;
				<input type="text" onChange={ 
					(e) => { 
						this.current_target = [];
						for (let i = 0; i < this.props.attributes.socket_count.value; ++i) {
							this.current_target.push(parseInt(e.target.value))
						}
					}
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
			build_schedule(this.props.attributes.socket_states.register, this.current_target, "create", true, {hour: this.current_hour, minute: this.current_minute}) 
					)
				} > Add </button>
			</span></p>	
			</div>	
		);
	}
}