# biblioteca padrão
from http import HTTPStatus

# bibliotecas de terceiros
from fastapi import FastAPI

# import do projeto
from fastapi_zero.database import get_all_users, get_user_count
from fastapi_zero.schemas import (
    Message,
    UserDB,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_zero.utils.validators import (
    check_already_registered_email,
    check_user_not_found,
)

app = FastAPI()


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_users(user: UserSchema):
    check_already_registered_email(user.email)

    user_with_id = UserDB(id=get_user_count() + 1, **user.model_dump())

    get_all_users().append(user_with_id)

    return user_with_id


@app.get('/users/', response_model=UserList)
def read_users():
    return {'users': get_all_users()}


@app.get('/users/{user_id}', response_model=UserPublic)
def read_user(user_id: int):
    check_user_not_found(user_id)
    user_with_id = get_all_users()[user_id - 1]

    return user_with_id


# PENDENTE: TENTAR COLOCAR ID INVALIDO
@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema):
    check_user_not_found(user_id)
    all_users = get_all_users()
    for edited_user in all_users:
        if (edited_user.email == user.email
                and int(edited_user.id) != int(user_id)):
            check_already_registered_email(user.email)
    user_with_id = UserDB(**user.model_dump(), id=user_id)

    get_all_users()[user_id - 1] = user_with_id

    return user_with_id


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int):
    check_user_not_found(user_id)

    del get_all_users()[user_id - 1]

    return {'message': 'User deleted'}


# if __name__ == '__main__':
#     uvicorn.run('app:app', host='0.0.0.0', port=8000)
