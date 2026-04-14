import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import settings
from pydantic import EmailStr

from mail.mailer import EmailData, Mailer


class SMTPMailService(Mailer):
    def __init__(
        self,
        smtp_server: str = settings.SMTP_SERVER,
        smtp_port: int = settings.SMTP_PORT,
        smtp_user: str = settings.SMTP_USER,
        smtp_password: str = settings.SMTP_PASSWORD,
        from_email: EmailStr = settings.SMTP_FROM_EMAIL,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email

    def send_html_email(self, email_data: EmailData) -> bool:
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = email_data.subject
            message["From"] = self.from_email
            message["To"] = email_data.recipient

            html_part = MIMEText(email_data.html_content, "html")
            message.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_port == 587:
                    server.starttls()

                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

                server.send_message(message)

            return True
        except Exception:
            return False
