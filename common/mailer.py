#!/usr/bin/env python3

import json, os, mimetypes,	smtplib
from email.message import EmailMessage
from typing	import Optional, List

CREDENTIALS	= os.path.dirname(os.path.realpath(__file__)) + "/.mailer.credentials"

def	load_credentials(path =	CREDENTIALS):
	if not os.path.exists(path):
		raise FileNotFoundError(f"Credentials file not found: {path}")

	with open(path,	"r", encoding = "utf-8") as f:
		return json.load(f)

def	create_email_message(
	sender:	str,
	recipients:	List[str],
	subject: str,
	body_text: str,
	body_html: Optional[str] = None,
	attachments: Optional[List[str]] = None,
) -> EmailMessage:
	msg	= EmailMessage()
	msg["From"]	= sender
	msg["To"] =	", ".join(recipients)
	msg["Subject"] = subject
	msg.set_content(body_text)

	if body_html:
		msg.add_alternative(body_html, subtype="html")

	if attachments:
		for	filepath in	attachments:
			if not os.path.exists(filepath):
				raise FileNotFoundError(f"Attachment not found:	{filepath}")
			ctype, encoding	= mimetypes.guess_type(filepath)
			if ctype is	None:
				ctype =	"application/octet-stream"
			maintype, subtype =	ctype.split("/", 1)
			with open(filepath,	"rb") as fp:
				data = fp.read()
			filename = os.path.basename(filepath)
			msg.add_attachment(data, maintype=maintype,	subtype=subtype, filename=filename)

	return msg

def	send_email(
	body_text: str,
	body_html: Optional[str] = None,
	recipients: List[str] = ["braeden.mulligan@gmail.com"],
	subject: str = "EasyDen Notification",
):
	smtp_host = "smtp.gmail.com"
	smtp_port = 587
	creds = load_credentials()
	sender_email = creds.get("email")
	app_password = creds.get("app_password")

	if not sender_email or not app_password:
		raise ValueError("credentials must contain 'email' and 'app_password' fields.")

	message = create_email_message(sender_email, recipients, subject, body_text, body_html=body_html)

	with smtplib.SMTP(smtp_host, smtp_port,	timeout=30) as smtp:
		smtp.ehlo()
		smtp.starttls()
		smtp.ehlo()
		smtp.login(sender_email, app_password)
		smtp.send_message(message)
