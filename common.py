import config

import datetime, os
import email.message, smtplib

# Wrapper for common pattern of error checking while opening/writing files.
def write_guard(f, mode, content):
	return

# Logger #
# Intended to be a reliable and robust tool for debugging, recording errors,
#   and monitoring server componenets for the SmartHome project.
#
# Holds and manages queued messages to be logged to a file or sent via email.
# "reports" are to be sent by email while "logs" are to be written to a file.
# Optional <size> parameter dictates the line capacity of the log file.
# Emails will automatically be sent when the email report buffer reaches
#   <max_email_reports> capacity. Currently the value is arbitrarily decided.
# Otherwise actual logging and email reports must be committed manually using
#   the <record_events()> method.
# Avoid giving multiple instances of the class the same file name <dest>. There
#   is no synchronization or thread safety in the design.
class Logger:

	max_email_reports = 16

	def __init__(self, dest, size=512):
		self.log_file = dest
		self.max_file_size = size
		self.logs = []
		# reports contains tuples of messages with priority (<string>, <bool>).
		# Priority indicates whether to log if email fails.
		self.reports = []

	def build_event(self, event):
		dt = datetime.datetime.now()
		prefix = dt.strftime("%Y-%m-%d-%H:%M, ")
		return prefix + event

	# If event will be both logged and reported, leave priority False. Otherwise
	#   email failures will cause redundant logs.
	def add_report(self, entry, priority=False):
		self.reports.append((self.build_event(entry), priority))
		if len(self.reports) >= self.max_email_reports:
			if self.send_email():
				del self.reports[:]
			else:
				for entry, priority in self.reports:
					if priority:
						self.logs.append(entry)

	def add_log(self, entry):
		self.logs.append(self.build_event(entry))

	def record_events(self, include_reports=True):
		n = len(self.logs)
		if n >= self.max_file_size:
			self.add_report("WARNING: Log buffer exceeded max log-file length.", True)

		if include_reports and self.reports:
			if not self.send_email():
				for entry, priority in self.reports:
					if priority:
						self.logs.append(entry)
				#self.add_log("ERROR: Failed to send email; writing reports as logs instead.")
				self.logs.sort()
			else:
				del self.reports[:]

		if not self.logs:
			return True
		# Append logs to end of file bumping oldest logs out of the file.
		# Only truncate logs immediately before writing.
		if n >= self.max_file_size:
			self.logs = self.logs[(n - self.max_file_size):]
		try:
			with open(self.log_file, "r+") as f_logs:
				line_count = sum(1 for line in f_logs)
				f_logs.seek(0)
				if line_count + n >= self.max_file_size:
					remaining_logs = f_logs.readlines()[(n + line_count - self.max_file_size):]
					f_logs.truncate(0)
					f_logs.seek(0)
					f_logs.write("".join(remaining_logs))
				else:
					f_logs.seek(0, 2)
					#f_logs.readlines()
				f_logs.write("\n".join(self.logs) + "\n")
			del self.logs[:]
		except FileNotFoundError:
			#TODO: a second FileNotFound indicates bad path.
			with open(self.log_file, "w") as f_logs:
				f_logs.write("\n".join(self.logs) + "\n")
		except Exception as e:
			self.add_report("ERROR: Logging has failed, " + str(e))
			return False
		return True

	# This may not need to be called during normal operation. Both logs and
	#   reports get cleared automatically after being recorded. 
	def erase_all(self):
		del self.logs[:]
		del self.reports[:]

	def send_email(self):
		try:
			with open(config.BASE_DIR + "status_files/email_credentials.txt", "r") as creds:
				CREDENTIALS = (creds.readline().strip(), creds.readline().strip())
		except Exception as e:
			self.add_log("ERROR: Failed to obtain email credentials. " + str(e))
			return False

		content = "Status Reports:\n"
		content += "\n".join([event[0] for event in self.reports]) + "\n"
		content += "\n- SmartHome Server\n"

		SENDER, PASSWORD = CREDENTIALS
		RECIPIENT = config.ADMIN_EMAIL 

		SUBJECT = "SmartHome Status Update"

		MSG = email.message.Message()
		MSG["From"] = SENDER
		MSG["To"] = RECIPIENT
		MSG["Subject"] = SUBJECT
		MSG.set_payload(content)

		HOST = "smtp.gmail.com"
		PORT = 587

		try:
			server = smtplib.SMTP(host=HOST, port=PORT)
			server.ehlo()
			server.starttls()
			server.login(SENDER, PASSWORD)

			server.sendmail(SENDER, [RECIPIENT], MSG.as_string())
			server.quit()
		except Exception as e:
			self.add_log("ERROR: smtplib, " + str(e))
			return False
		return True
