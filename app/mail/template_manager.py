from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from models.user import User
from pydantic import EmailStr

from mail.mailer import EmailData


class EmailTemplateManager:
    def __init__(
        self,
        template_dir: str | Path = Path(Path(__file__).parent).joinpath(
            "email-templates"
        ),
    ):
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
        )

    def __render_template(
        self,
        template_name: str,
        recipient: EmailStr,
        subject: str,
        **context,
    ) -> EmailData:
        template = self.env.get_template(template_name)
        html_content = template.render(**context)
        return EmailData(
            recipient=recipient,
            subject=subject,
            html_content=html_content,
        )

    def welcome_email(
        self,
        user: User,
    ) -> EmailData:
        return self.__render_template(
            template_name="welcome.html",
            recipient=user.email,
            subject="Welcome to RefIn!",
            name=user.name,
        )

    def email_verification_email(
        self,
        user: User,
        verification_link: str,
    ) -> EmailData:
        return self.__render_template(
            template_name="email_verification.html",
            recipient=user.email,
            subject="Email Verification",
            name=user.name,
            verification_link=verification_link,
        )

    def password_reset_email(
        self,
        user: User,
        reset_link: str,
        expiration_minutes: int = 10,
    ) -> EmailData:
        return self.__render_template(
            template_name="password_reset.html",
            recipient=user.email,
            subject="Reset your password",
            name=user.name,
            reset_link=reset_link,
            expiration_minutes=expiration_minutes,
        )

    def password_updated(
        self,
        user: User,
    ) -> EmailData:
        return self.__render_template(
            template_name="password_updated.html",
            recipient=user.email,
            subject="Your password is updated",
            name=user.name,
        )
