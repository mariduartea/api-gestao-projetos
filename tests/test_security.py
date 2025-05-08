from http import HTTPStatus

from jwt import decode

from task_flow.security import create_access_token, settings


def test_jwt():
    data = {'sub': 'test@test.com'}  # sub é o padrão do JWT para o usuário
    token = create_access_token(data)
    # o token é gerado com o email do usuário

    result = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert result['sub'] == data['sub']
    assert result['exp']


def test_jwt_invalid_token(client):
    respose = client.delete(
        '/users/100', headers={'Authorization': 'Bearer token-invalido'}
    )
    assert respose.status_code == HTTPStatus.UNAUTHORIZED
    assert respose.json() == {'detail': 'Credenciais inválidas'}


def test_get_current_user_email_not_autorized(client):
    data = {'no-email': 'teste'}
    # no-email não é o padrão do JWT para o usuário
    token = create_access_token(data)

    respose = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )  # o token é gerado com o email do usuário

    assert respose.status_code == HTTPStatus.UNAUTHORIZED
    assert respose.json() == {'detail': 'Credenciais inválidas'}


def test_get_current_user_user_not_autorized(client):
    data = {'sub': 'teste@teste'}  # teste@teste não é um usuário válido
    token = create_access_token(data)

    respose = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert respose.status_code == HTTPStatus.UNAUTHORIZED
    assert respose.json() == {'detail': 'Credenciais inválidas'}
