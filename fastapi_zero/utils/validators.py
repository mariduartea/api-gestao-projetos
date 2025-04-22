from http import HTTPStatus

from fastapi import HTTPException

from fastapi_zero.database import get_user_by_email


def check_already_registered_email(email: str):
    if get_user_by_email(email):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Email already registered"
        )
