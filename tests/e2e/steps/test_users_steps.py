from http import HTTPStatus

import pytest
from conftest import UserFactory
from pytest_bdd import given, parsers, scenarios, then, when

from task_flow.security import get_password_hash

scenarios('../feature/users.feature')


@pytest.fixture
def context():
    return {}


@given(
    parsers.parse(
        'um usuário chamado "{username}" '
        'com email "{email}" e senha "{password}"'
    )
)
def criar_usuario(session, context, username, email, password):
    hashed = get_password_hash(password)
    user = UserFactory(username=username, email=email, password=hashed)
    session.add(user)
    session.commit()
    session.refresh(user)

    context['user_id'] = user.id
    context['username'] = username
    context['email'] = email
    context['password'] = password


@given(
    parsers.parse(
        'um time chamado "{team_name}" é criado com o usuário "{username}"'
    )
)
def criar_time(client, context, team_name, username):
    # Autentica o usuário
    res = client.post(
        '/auth/token',
        data={'username': context['email'], 'password': context['password']},
    )
    assert res.status_code == HTTPStatus.OK
    token = res.json()['access_token']
    context['headers'] = {'Authorization': f'Bearer {token}'}
    context['team_name'] = team_name

    # Cria o time via API
    res = client.post(
        '/teams/',
        json={'team_name': team_name, 'user_list': [username]},
        headers=context['headers'],
    )
    assert res.status_code == HTTPStatus.CREATED


@when(
    parsers.parse(
        'o usuário "{old_username}" altera seu nome para "{new_username}"'
    )
)
def atualizar_usuario(client, context, old_username, new_username):
    res = client.put(
        f'/users/{context["user_id"]}',
        json={
            'username': new_username,
            'email': context['email'],
            'password': context['password'],
        },
        headers=context['headers'],
    )
    assert res.status_code == HTTPStatus.OK
    context['username'] = new_username


@then(
    parsers.parse(
        'o time "{team_name}" deve listar "{expected_username}" como membro'
    )
)
def verificar_membro_no_time(client, context, team_name, expected_username):
    res = client.get('/teams/', headers=context['headers'])
    assert res.status_code == HTTPStatus.OK
    teams = res.json().get('teams', [])

    # Encontra o time pelo nome
    time = next((t for t in teams if t['team_name'] == team_name), None)
    assert time is not None, f"Time '{team_name}' não encontrado."

    membros = time['users']
    assert expected_username in membros, f"'{expected_username}' "
    +f'não está entre os membros: {membros}'
