import pathlib
import secrets
import warnings
from typing import Literal
from urllib.parse import urljoin

from pydantic import (
    EmailStr,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


class Settings(BaseSettings):
    configPath: pathlib.Path = pathlib.Path(__file__)
    rootProject: pathlib.Path = pathlib.Path(configPath.parent).parent

    envFile: pathlib.Path = rootProject.joinpath(".env")
    if not envFile.is_file():
        raise FileNotFoundError(
            "envFile (.env) does not exists at the root of the project."
        )

    model_config = SettingsConfigDict(
        env_file=str(envFile),
        env_ignore_empty=True,
        extra="ignore",
    )

    # TODO: Update to API_VERSION_1_STRING
    API_VERSION_1_STRING: str = "/api/v1"

    SECRET_KEY: str = secrets.token_urlsafe(nbytes=32)

    # Dummy hash to use for timing attack prevention when user is not found
    # This is an Argon2 hash of a random password, used to ensure constant-time comparison
    DUMMY_PASSWORD_HASH: str = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    FRONTEND_URL: str = "http://localhost:5173/"
    FRONTEND_PASSWORD_RESET_PATH: str = "/password-reset"

    @computed_field
    @property
    def FRONTEND_PASSWORD_RESET_URL(self) -> str:
        return urljoin(
            self.FRONTEND_URL.rstrip("/") + "/", self.FRONTEND_PASSWORD_RESET_PATH
        )

    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 10

    PROJECT_NAME: str

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    FIRST_ADMIN_EMAIL: EmailStr = "test@example.com"
    FIRST_ADMIN_PASSWORD: str
    FIRST_ADMIN_NAME: str

    # SMTP Configuration for email sending
    SMTP_SERVER: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: EmailStr = "noreply@example.com"

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f"The value of {var_name} is 'changethis'."
                "For security, please change it, at least for production."
            )

            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret("FIRST_ADMIN_PASSWORD", self.FIRST_ADMIN_PASSWORD)
        return self


settings = Settings()  # type: ignore
