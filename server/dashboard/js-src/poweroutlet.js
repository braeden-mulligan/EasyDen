
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
