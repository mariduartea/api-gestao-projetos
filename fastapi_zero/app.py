# biblioteca padrão

from http import HTTPStatus

# blbliotecas terceiras
from fastapi import FastAPI, HTTPException

# import do projeto
from fastapi_zero.database import get_all_users, get_user_count
from fastapi_zero.schemas import (
    Message,
    UserDB,
    UserList,
    UserPublic,
    UserSchema,
)

app = FastAPI()


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_users(user: UserSchema):
    user_with_id = UserDB(id=get_user_count() + 1, **user.model_dump())

    get_all_users().append(user_with_id)

    return user_with_id


@app.get('/users/', response_model=UserList)
def read_users():
    return {'users': get_all_users()}


@app.get('/users/{user_id}', response_model=UserPublic)
def read_user(user_id: int):
    if user_id < 1 or user_id > get_user_count():
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    user_with_id = get_all_users()[user_id - 1]

    return user_with_id


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema):
    if user_id < 1 or user_id > get_user_count():
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user_with_id = UserDB(**user.model_dump(), id=user_id)

    get_all_users()[user_id - 1] = user_with_id

    return user_with_id


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int):
    if user_id < 1 or user_id > get_user_count():
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    del get_all_users()[user_id - 1]

    return {'message': 'User deleted'}
