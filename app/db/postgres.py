from config import settings
from models import (
    email_verification,  # noqa: F401
    password_reset,  # noqa: F401
    user,  # noqa: F401
    user_certificate,  # noqa: F401
    user_education,  # noqa: F401
    user_experience,  # noqa: F401
    user_language,  # noqa: F401
    user_link,  # noqa: F401
    user_profile,  # noqa: F401
    user_project,  # noqa: F401
    user_skill,  # noqa: F401
)
from sqlmodel import create_engine

# Make sure all SQLModels are imported from (models)
# before initializing the database otherwise, SQLModel
# might fail.
# See: https://github.com/fastapi/full-stack-fastapi-template/issues/28

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
