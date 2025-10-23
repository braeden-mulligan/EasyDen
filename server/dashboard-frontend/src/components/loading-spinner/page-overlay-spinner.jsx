import { z_indices } from "../../defines";

const styles = {
	loading_overlay: {
		position: "absolute",
		inset: 0,
		backgroundColor: "rgba(255, 255, 255, 0.8)",
		display: "flex",
		justifyContent: "center",
		alignItems: "center",
		PointerEvents: "none",
		zIndex: z_indices.overlay
	},
	spinner: {
		width: "48px",
		height: "48px",
		border: "5px solid #d1d5db",
		borderTop: "5px solid #3b82f6",
		borderRadius: "50%",
		animation: "spin 1s linear infinite"
	},
	css: `
		@keyframes spin {
			0% {
				transform: rotate(0deg);
			}
			100% {
				transform: rotate(360deg);
			}
		}
	`
};

export const PageOverlaySpinner = function() {
	return (
		<>
			<div style={styles.loading_overlay}>
				<div style={styles.spinner}></div>
			</div>
			<style>{styles.css}</style>
		</>
	);
};