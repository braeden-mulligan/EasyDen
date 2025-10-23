import { useState } from "react";
import { PageBlocker } from "../components/loading-spinner/page-overlay-spinner";
import { request } from "../api";
import { add_notification } from "../store";
import { store_jwt_expiry } from "../utils";

const styles = {
	login_container: {
		height: "100vh",
		display: "flex",
		justifyContent: "center",
		alignItems: "center",
		backgroundColor: "#f3f4f6",
		position: "relative"
	},
	login_box: {
		backgroundColor: "white",
		padding: "2rem",
		borderRadius: "12px",
		boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
		width: "320px",
		textAlign: "center",
		transition: "opacity 0.2s ease"
	},
	login_box_disabled: {
		opacity: 0.6,
		pointerEvents: "none"
	},
	title: {
		marginBottom: "1.5rem",
		color: "#333",
	},
	form: {
		display: "flex",
		flexDirection: "column",
		gap: "0.75rem",
		textAlign: "left",
	},
	label: {
		fontSize: "0.9rem",
		color: "#555",
	},

	input_field: {
		padding: "0.6rem",
		border: "1px solid #ccc",
		borderRadius: "6px",
		fontSize: "1rem",
		backgroundColor: "white",
	},

	button: {
		marginTop: "1rem",
		backgroundColor: "#3b82f6",
		color: "white",
		border: "none",
		padding: "0.7rem",
		borderRadius: "6px",
		fontSize: "1rem",
		cursor: "pointer",
		transition: "background-color 0.2s ease, transform 0.1s ease"
	},
	css: `
		input:focus {
			border-color: #3b82f6;
			outline: none;
			box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
		}

		button:hover {
			background-color: #2563eb;
			transform: translateY(-1px);
		}

		button:disabled {
			background-color: #93c5fd;
			cursor: not-allowed;
		}

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

export const LoginPage = function() {
	const [username, set_username] = useState("");
	const [password, set_password] = useState("");
	const [loading, set_loading] = useState(false);

	const handle_submit = async function(e) {
		e.preventDefault();
		set_loading(true);

		let login_success = false;

		try {
			const login_result = await request({
				action: "login",
				username: username,
				password: password
			}, null, "/auth");

			if (login_result?.result == "success") {
				store_jwt_expiry(login_result.tokens.access, login_result.tokens.refresh);
				login_success = true;
			} else {
				login_result?.error && add_notification(`Login failed: ${login_result.error.details}`);
			}
		} catch (error) {
			add_notification(`Unhandled login error: ${error.message}`);
			console.error("Login error:", error);
		} finally {
			set_loading(false)
		}

		if (login_success) window.location.reload();
	};

return (
	<div style={styles.login_container}>
		{loading && <PageBlocker spinner />}
		<div style={{ ...styles.login_box, ...(loading && styles.login_box_disabled) }}>
			<h2 style={styles.title}>Log In</h2>
			<form style={styles.form} onSubmit={handle_submit}>
				<label style={styles.label}>Username</label>
				<input type="text" value={username} onChange={(e) => set_username(e.target.value)} required disabled={loading} style={styles.input_field}/>

				<label style={styles.label}>Password</label>
				<input type="password" value={password} onChange={(e) => set_password(e.target.value)} required disabled={loading} style={styles.input_field}/>

				<button type="submit" disabled={loading} style={styles.button}>
					{loading ? "Signing in..." : "Sign In"}
				</button>
			</form>
		</div>
		<style>{styles.css}</style>
	</div>
	);
}