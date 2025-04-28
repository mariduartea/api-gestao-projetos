from http import HTTPStatus

from jwt import decode

from fastapi_zero.security import create_acess_token, settings


def test_jwt():
    data = {'sub': 'test@test.com'}
    token = create_acess_token(data)

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
