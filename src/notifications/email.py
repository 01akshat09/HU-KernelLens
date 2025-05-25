from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from jinja2 import Template
from config.settings import EMAIL_CONFIG

def send_email_alert(alarm_data, alarm_type):
    """Send an email alert for high CPU utilization."""
    with open("templates/email_template.html", "r") as f:
        template = Template(f.read())
    
    
    message = ""
    SUBJECT = f"{alarm_type} detected - Please investigate"

    if alarm_type == "CPU":
        message = "High CPU utilization has been detected for the following process(es)."
    elif alarm_type == "User Activity":
        message = "Suspicious user activity detected."
    elif alarm_type == "Privileged Process":
        message = "Privileged process activity detected."
    else:
        message = "Alert from monitoring system."

    html_content = template.render(
        alarm_type=alarm_type,
        message=message,
        alarm_data=alarm_data
    )

    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_CONFIG["from"]
    msg['To'] = EMAIL_CONFIG["to"]
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_CONFIG["from"], EMAIL_CONFIG["password"])
        server.sendmail(EMAIL_CONFIG["from"], EMAIL_CONFIG["to"], msg.as_string())
        server.quit()
        print("Successfully sent the mail")
    except Exception as e:
        print(f"Failed to send mail: {e}")