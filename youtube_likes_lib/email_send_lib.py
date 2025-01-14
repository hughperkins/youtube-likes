import smtplib
from email.mime.text import MIMEText

from youtube_likes_lib.yl_types import Config, Output


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


def merge_channel_mails(outputs: list[Output]) -> tuple[str, str]:
    print("merge_channel_mails")
    global_email_message = ""
    global_priority_reasons_title = ""
    global_email_message_l = []
    # for res in results:
    for output in outputs:
        print("output", output)
        # output: Output = res["output"]
        # _body = res["body"]
        if output.body != "":
            # _priority_reasons_title = output.priority_reasons_title
            global_email_message_l.append(output.email_message)
            if output.priority_reasons_title != "":
                output.priority_reasons_title = output.priority_reasons_title.strip()
                # global_priority_reasons_title += f" {channel_abbrev}[{output.priority_reasons_title}]"
                global_priority_reasons_title += f" {output.priority_reasons_title}"
    global_email_message = "\n".join(global_email_message_l)
    return global_priority_reasons_title, global_email_message


def send_smtp(config: Config, subject_postfix: str, body: str) -> None:
    subject = config.smtp_subject
    subject += subject_postfix
    # print(config)
    send_email(
        config.smtp_server,
        config.smtp_port,
        config.smtp_username,
        config.smtp_password,
        config.smtp_from_email,
        config.smtp_to_email,
        subject,
        body,
    )


def generate_email_message(channel_name: str, channel_abbrev: str, output: Output) -> None:
    """
    populates email_message and priority_reasons_title
    """
    output.email_message = ""
    if output.body != "":
        output.email_message += channel_name + "\n"
        output.email_message += "=" * len(channel_name) + "\n"
        output.email_message += "\n"
        if output.is_priority:
            output.email_message += "Priority changes:\n"
            output.email_message += output.priority_reasons_desc
            output.email_message += "\n"
        output.email_message += "Details:\n"
        output.email_message += output.body
        # email_message += "\n"
    if output.priority_reasons_title != "":
        output.priority_reasons_title = output.priority_reasons_title.strip()
        output.priority_reasons_title = f" {channel_abbrev}[{output.priority_reasons_title}]"
