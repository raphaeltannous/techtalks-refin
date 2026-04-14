from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import EmailStr


@dataclass
class EmailData:
    recipient: EmailStr
    subject: str
    html_content: str


class Mailer(ABC):
    @abstractmethod
    def send_html_email(self, email_data: EmailData) -> bool:
        pass
