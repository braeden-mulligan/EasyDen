import "./toggle-switch.css"

export const ToggleSwitch = function({ style, disabled }) {
	return (
		<div style={style}>
			<label class="toggle-switch">
				<input type="checkbox" disabled={disabled}/>
				<span class="toggle-slider"/>
			</label>
		</div>
	)
}