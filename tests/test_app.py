# biblioteca padrão
from http import HTTPStatus

# import do projeto
from fastapi_zero.database import get_user_count


# teste para criar um usuário com sucesso
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


# teste para validar que não é possível inserir senha menor que 6 caracteres
def test_not_create_user_password_less_than_6(client):
    response = client.post(
        '/users/',
        json={
            'username': 'testusername',
            'email': 'teste01@teste.com',
            'password': '12345'
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # Verifica se existe um erro relacionado ao campo "password"
    assert any(
        error["loc"][-1] == "password" and
        error["msg"] == "Value error, Password must have at least 6 characters"
        for error in response.json()["detail"]
    )


# teste para validar que não é possível cadastrar 2 usuários com o mesmo email
# teste para ler usuários com sucesso
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


# teste para ler um único usuário
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


# teste para validar que não é possível ter id menor que 1
def test_read_invalid_user_id_less_than_1(client):
    response = client.get(
        '/users/0',
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


# validar de ID maior que total de usuários
def test_read_invalid_user_id_grater_than_length(client):
    response = client.get(
        '/users/' + str(get_user_count() + 1)
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


# teste para editar um usuario com sucesso
def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'testusername02',
            'email': 'teste@teste.com',
            'password': 'password',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'testusername02',
        'email': 'teste@teste.com',
        'id': 1,
    }


# validar edição com ID fora do limite (menor)
def test_update_user_with_invalid_id_less_than_1(client):
    response = client.put(
        '/users/0',
        json={
            'username': 'testusername02',
            'email': 'teste@teste.com',
            'password': 'password'
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


# validar edição com ID fora do limite (maior)
def test_update_user_with_invalid_id_grater_than_length(client):
    response = client.put(
        '/users/' + str(get_user_count() + 1),
        json={
            'username': 'testusername02',
            'email': 'teste@teste.com',
            'password': 'password'
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


# teste para deletar usuário com sucesso
def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.json() == {'message': 'User deleted'}


# validar deleção com ID fora do limite (menor)
def test_delete_user_with_invalid_id_less_than_1(client):
    response = client.delete(
        '/users/0'
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


# validar deleção com ID fora do limite (maior)
def test_delete_user_with_invalid_id_grater_than_length(client):
    response = client.delete(
        '/users/' + str(get_user_count() + 1)
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
