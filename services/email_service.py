import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class EmailService:
    def __init__(self):
        self.user = settings.GMAIL_USER
        self.password = settings.GMAIL_APP_PWD
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        if not self.user or not self.password:
            logger.warning("Email credentials are missing.")

    def send_email_batch(self, subject, body, receivers):
        """Sends an email to a list of receivers using BCC."""
        if not receivers:
            logger.info("No receivers for email.")
            return

        msg = MIMEMultipart()
        sender_name = "RevolTac"
        msg['From'] = f"{sender_name} <{self.user}>"
        msg['Subject'] = subject
        msg['Bcc'] = ", ".join(receivers)
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(msg)
            server.quit()
            logger.info(f"✅ Email sent successfully to {len(receivers)} recipients.")
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")

    def send_admin_alert(self, subject, body, admin_email="ksmsk0701@gmail.com"):
        """Sends an alert email to the admin."""
        self.send_email_batch(subject, body, [admin_email])
