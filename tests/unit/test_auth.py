from http import HTTPStatus

import pytest
from freezegun import freeze_time

pytestmark = pytest.mark.unit


def test_get_token(client, user):
    response = client.post(
        'auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_token_expired_after_time(client, user):
    with freeze_time('2025-01-01 12:00:00'):
        # gerar o token (12:00)
        response = client.post(
            'auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']
        # a gente pega o token que foi gerado para o meio dia

    with freeze_time('2025-01-01 12:31:00'):
        # Usa o token (12:31)
        response = client.put(
            f'users/{user.id}',
            # o user é o mesmo que usamos para criar o token
            # mas o tempo está 31 minutos na frente
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrong_username',
                'password': 'wrong_password',
                'email': 'wrong_email',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Credenciais inválidas'}


def test_token_wrong_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_password'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid username or password'}


def test_token_wrong_email(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'test@test.com', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid username or password'}


def test_refresh_wrong_email(client, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh(client, user):
    with freeze_time('2025-01-01 12:00:00'):
        # gerar o token (12:00)
        response = client.post(
            'auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']
        # a gente pega o token que foi gerado para o meio dia

    with freeze_time('2025-01-01 12:31:00'):
        # Usa o token (12:31)
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Credenciais inválidas'}
