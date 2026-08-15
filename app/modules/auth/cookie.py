from fastapi import Response

from app.core.config import settings
from app.modules.auth.dto import CookieConfig


class AuthCookie:
    ACCESS = "access_token"
    REFRESH = "refresh_token"


    ACCESS_PATH = "/"
    REFRESH_PATH = "/api/auth/refresh"


    CONFIG = {
        ACCESS: CookieConfig(path=ACCESS_PATH, max_age=settings.security.access_token_expire_seconds),
        REFRESH: CookieConfig(path=REFRESH_PATH, max_age=settings.security.refresh_token_expire_seconds),
    }

    @classmethod
    def _set(cls,response: Response,name: str,token: str) -> None:
        config = cls.CONFIG[name]

        response.set_cookie(
            key=name,
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            path=config.path,
            max_age=config.max_age,
        )

    @classmethod
    def set_access(cls, response: Response, token: str) -> None:
        cls._set(response, cls.ACCESS, token)

    @classmethod
    def set_refresh(cls, response: Response, token: str) -> None:
        cls._set(response, cls.REFRESH, token)

    @classmethod
    def clear(cls, response: Response) -> None:
        for name, config in cls.CONFIG.items():
            response.delete_cookie(key=name, path=config.path)