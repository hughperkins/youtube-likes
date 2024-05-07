import smtplib
from email.mime.text import MIMEText


def send_email(
    smtp_server,
    smtp_port,
    username,
    password,
    from_email,
    to_email,
    subject,
    message,
):
    msg = MIMEText(
        "<html><body>"
        + message.replace(" ", "&nbsp;").replace("\n", "<br />")
        + "</body></html>",
        "html",
    )
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.login(username, password)
        smtp.sendmail(from_email, to_email, msg.as_string())
