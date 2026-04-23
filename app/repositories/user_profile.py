import uuid
from abc import ABCMeta, abstractmethod

from models.user_profile import UserProfile


class UserProfileRepository:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> UserProfile | None:
        pass
