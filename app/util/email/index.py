import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

from app.util.setting import get_settings

settings = get_settings()
env = Environment(loader=FileSystemLoader("app/util/email/templates"))


def render_invoice_html(data: dict, template_name: str) -> str:

    template = env.get_template(template_name)
    return template.render(data=data)


def send_email(subject: str, to_email: str, html_body: str):
    # SMTP settings (replace with your SMTP config or use SendGrid/SES)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email

    # Add HTML content
    html_part = MIMEText(html_body, "html")
    msg.attach(html_part)
    try:
        # Create SMTP connection
        server = smtplib.SMTP(settings.EMAIL_HOST, int(settings.EMAIL_PORT))
        server.starttls()
        server.login(settings.EMAIL_FROM, settings.EMAIL_PASSWORD)

        # Send email
        server.send_message(msg)
        server.quit()
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return {"status": "error", "message": str(e)}
