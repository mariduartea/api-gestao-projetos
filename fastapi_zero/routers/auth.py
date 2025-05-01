from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import Token
from fastapi_zero.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

T_Session = Annotated[Session, Depends(get_session)]
T_OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
def login_for_access_token(session: T_Session, form_data: T_OAuthForm):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Usuário ou senha inválidos',
        )

    # a Claim sub é o padrão do JWT para o usuário
    # o token é gerado com o email do usuário
    access_token = create_access_token(data={'sub': user.email})

    return {
        'access_token': access_token,
        'token_type': 'Bearer',  # bearer é o padrão do OAuth2
    }


@router.post('/refresh_token', response_model=Token)
# aqui estamos apenas criando um novo token para o usuário já autenticado
def refresh_access_token(
    user: User = Depends(get_current_user),
):
    new_access_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'bearer'}
