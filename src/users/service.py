import logging

from starlette import status

from src.dao import DAO
from src.exceptions import CredentialsException
from src.users.models import User

logger = logging.getLogger("app")


class UserService:

    @classmethod
    async def search_user(cls, username, db):
        user = await DAO.search_by_fields(User, dict(username=username), db)
        if not user:
            message = f"Пользователь {username} не найден"
            logger.warning(message)
            raise CredentialsException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )
        return user
