# biblioteca padrão
from http import HTTPStatus

import pytest

# import do projeto
from task_flow.database import get_user_count
from task_flow.schemas import UserPublic

pytestmark = pytest.mark.unit


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'bolinha_teste',
            'email': 'bolinha@teste.com',
            'password': 'password',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['username'] == 'bolinha_teste'
    assert data['email'] == 'bolinha@teste.com'


def test_not_create_user_already_registered(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'bolinha@teste.com',
            'password': 'password',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already registered'}


def test_not_create_email_already_registered(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'bolinha',
            'email': user.email,
            'password': 'password',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already registered'}


# teste para validar que não é possível inserir senha menor que 6 caracteres
def test_not_create_user_password_less_than_6(client):
    response = client.post(
        '/users/',
        json={
            'username': 'testusername',
            'email': 'teste01@teste.com',
            'password': '12345',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # Verifica se existe um erro relacionado ao campo "password"
    assert any(
        error['loc'][-1] == 'password'
        and error['msg']
        == 'Value error, Password must have at least 6 characters'
        for error in response.json()['detail']
    )


# teste para ler usuários com sucesso
def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_one_user(client, user):
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': user.username,
        'email': user.email,
        'id': user.id,
    }


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


# teste para validar que não é possível ter id menor que 1
def test_not_read_invalid_user_id_less_than_1(client):
    response = client.get(
        '/users/0',
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


# validar de ID maior que total de usuários
def test_not_read_invalid_user_id_grater_than_length(client, session):
    response = client.get('/users/' + str(get_user_count(session) + 1))

    assert response.status_code == HTTPStatus.NOT_FOUND


# teste para editar um usuario com sucesso
def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'testusername02',
            'email': 'teste@teste.com',
            'password': 'teste123',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'testusername02',
        'email': 'teste@teste.com',
        'id': user.id,
    }


# teste para editar um usuario sem permissão
def test_not_update_wrong_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'testusername02',
            'email': 'teste@teste.com',
            'password': 'teste123',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'You are not allowed to edit this user'
    }


# teste para impedir edição com senha menor que 6 caracteres
def test_not_update_user_password_less_than_6(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': user.username,
            'email': user.email,
            'password': '12345',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    # Verifica se existe um erro relacionado ao campo "password"
    assert any(
        error['loc'][-1] == 'password'
        and error['msg']
        == 'Value error, Password must have at least 6 characters'
        for error in response.json()['detail']
    )


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_not_delete_wrong_user(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}',
        # other user é o usuário que não é o dono do token criado no conftest
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'You are not allowed to delete this user'
    }
