from starlette import status

from src.dao import DAO
from src.exceptions import CredentialsException
from src.users.models import User


class UserService:

    @classmethod
    async def search_user(cls, username, db):
        user = await DAO.search_by_fields(User, dict(username=username), db)
        if not user:
            raise CredentialsException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь {username} не найден",
            )
        return user
