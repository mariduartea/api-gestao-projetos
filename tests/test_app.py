# biblioteca padrão
from http import HTTPStatus

# import do projeto
from fastapi_zero.database import get_user_count


def test_create_user(client):
    response = client.post(  # UserSchema
        '/users/',
        json={
            'username': 'testusername',
            'email': 'teste@teste.com',
            'password': 'password',
        },
    )

    # Voltou o status code correto?
    assert response.status_code == HTTPStatus.CREATED
    # Validar o UserPublic
    assert response.json() == {
        'username': 'testusername',
        'email': 'teste@teste.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'username': 'testusername',
                'email': 'teste@teste.com',
                'id': 1,
            }
        ]
    }


def test_read_valid_user(client):
    response = client.get(
        '/users/1',
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'testusername',
        'email': 'teste@teste.com',
        'id': 1,
    }


def test_read_invalid_user_id_less_than_1(client):
    response = client.get(
        '/users/1',
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


# def test_read_invalid_user_id_grater_than_length():

def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'testusername02',
            'email': 'teste@teste.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'testusername02',
        'email': 'teste@teste.com',
        'id': 1,
    }


def test_update_user_with_invalid_id_less_than_1(client):
    response = client.put(
        '/users/0',
        json={
            'username': 'testusername02',
            'email': 'teste@teste.com',
            'password': '123'
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user_with_invalid_id_grater_than_length(client):
    response = client.put(
        '/users/' + str(get_user_count() + 1),
        json={
            'username': 'testusername02',
            'email': 'teste@teste.com',
            'password': '123'
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.json() == {'message': 'User deleted'}


def test_delete_user_with_invalid_id_less_than_1(client):
    response = client.delete(
        '/users/0'
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_with_invalid_id_grater_than_length(client):
    response = client.delete(
        '/users/' + str(get_user_count() + 1)
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
