import uuid
from abc import ABCMeta, abstractmethod
from typing import Sequence

from models.user_link import UserLink, UserLinkUpdate


class UserLinkRepository:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_all_by_user_profile_id(
        self,
        user_profile_id: uuid.UUID,
    ) -> Sequence[UserLink]:
        pass

    @abstractmethod
    def get_by_id(
        self,
        link_id: uuid.UUID,
    ) -> UserLink | None:
        pass

    @abstractmethod
    def add(
        self,
        link_in: UserLink,
    ) -> UserLink:
        pass

    @abstractmethod
    def update(
        self,
        link_db: UserLink,
        link_in: UserLinkUpdate,
    ) -> UserLink:
        pass

    @abstractmethod
    def delete(
        self,
        link_db: UserLink,
    ) -> None:
        pass
