from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from jinja2 import Template
from config.settings import EMAIL_CONFIG

def send_email_alert(cpu_alarms):
    """Send an email alert for high CPU utilization."""
    with open("templates/email_template.html", "r") as f:
        template = Template(f.read())
    
    html_content = template.render(
        alert_type="CPU Alert",
        message="High CPU utilization has been detected for the following process. Kindly investigate the cause to prevent potential performance issues.",
        cpu_alarms=cpu_alarms
    )

    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_CONFIG["from"]
    msg['To'] = EMAIL_CONFIG["to"]
    msg['Subject'] = "High CPU utilization detected - Please investigate"
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