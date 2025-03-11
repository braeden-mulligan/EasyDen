import { useStore } from "../store"

export const NotificationSnackbar = function() {
	console.log("notification rendered")
	const notifications = useStore((state) => state.notifications)
	const clear_notifications = useStore((state) => state.clear_notifications);

	if (!notifications.length) return null

	return (
		<div style={{ position: "fixed", bottom: "32px", right: "32px"}}>
			<h3>Notifications:</h3>
			{ notifications.map((notification) => <p>{ JSON.stringify(notification) }</p> ) }
			<button onClick={clear_notifications}>Clear</button>
		</div>
	)
}