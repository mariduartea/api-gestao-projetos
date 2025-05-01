from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.settings import Settings

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
settings = Settings()
T_Session = Annotated[Session, Depends(get_session)]


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# data é um dicionário com os dados do usuário
def create_access_token(data: dict):
    to_encode = data.copy()

    # adiciona um tempo de 30 minutos para o token expirar
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    # exp é uma Claim padrão do JWT
    to_encode.update({'exp': expire})
    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def get_current_user(
    session: T_Session,
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Credenciais inválidas',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get('sub')
        if not username:
            raise credentials_exception

    except ExpiredSignatureError:
        # o ExpiredSignatureError é uma exceção encapsulada do PyJWTError
        # o token expirou, então a gente não pode usar mais ele
        raise credentials_exception

    except PyJWTError:
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == username))

    if not user:
        raise credentials_exception

    return user
