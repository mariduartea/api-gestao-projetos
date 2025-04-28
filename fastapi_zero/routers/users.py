from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', response_model=UserList)
def read_users(session: T_Session, limit: int = 10, skip: int = 0):
    user = session.scalars(select(User).limit(limit).offset(skip)).all()
    return {'users': user}


@router.get('/{user_id}', response_model=UserPublic)
def read_user_with_id(user_id: int, session: T_Session):
    user_with_id = session.scalar(select(User).where(User.id == user_id))

    if not user_with_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado'
        )

    return user_with_id


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_users(user: UserSchema, session: T_Session):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Usuário já cadastrado',
            )

        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email já cadastrado',
            )

    db_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


# PENDENTE: TENTAR COLOCAR ID INVALIDO
@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você não tem permissão para editar esse usuário',
        )

    current_user.username = user.username
    current_user.password = get_password_hash(user.password)
    current_user.email = user.email

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você não tem permissão para deletar esse usuário',
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'Usuário deletado com sucesso'}
