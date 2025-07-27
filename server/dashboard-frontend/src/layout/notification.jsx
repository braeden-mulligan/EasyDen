import { useGlobalStore } from "../store"

export const NotificationSnackbar = function() {
	const notifications = useGlobalStore((state) => state.notifications)
	const clear_notifications = useGlobalStore((state) => state.clear_notifications);

	if (!notifications.length) return null

	return (
		<div style={{ position: "fixed", bottom: "32px", right: "32px"}}>
			<h3>Notifications:</h3>
			{ notifications.map((notification) => <p>{ JSON.stringify(notification) }</p> ) }
			<button onClick={clear_notifications}>Clear</button>
		</div>
	)
}