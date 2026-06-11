from fastapi import HTTPException
from starlette import status


class CredentialsException(HTTPException):
    def __init__(
        self,
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail: str = "Не удалось валидировать учетные данные",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
