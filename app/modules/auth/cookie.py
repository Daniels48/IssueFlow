from fastapi import Response

from app.core.config import settings

from typing import Literal


CookieName = Literal["access_token", "refresh_token"]


ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
PATH_ACCESS_COOKIE = "/"
PATH_REFRESH_COOKIE = "/api/auth/refresh"


COOKIE_CONFIG = {
    ACCESS_COOKIE: {
        "path": PATH_ACCESS_COOKIE,
        "max_age": settings.security.access_token_expire_seconds,
    },
    REFRESH_COOKIE: {
        "path": PATH_REFRESH_COOKIE,
        "max_age": settings.security.refresh_token_expire_seconds,
    },
}

def _set_cookie(response: Response, token:str, name_cookie:str) -> None:
    data = COOKIE_CONFIG[name_cookie]
    response.set_cookie(
        key=name_cookie,
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        path=data["path"],
        max_age=data["max_age"],
    )

def set_access_cookie(response: Response,access_token: str) -> None:
    _set_cookie(response=response, name_cookie=ACCESS_COOKIE, token=access_token)


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    _set_cookie(response=response, name_cookie=REFRESH_COOKIE, token=refresh_token)


def clear_auth_cookies(response: Response) -> None:
    for cookie_name, config in COOKIE_CONFIG.items():
        response.delete_cookie(
            key=cookie_name,
            path=config["path"],
        )