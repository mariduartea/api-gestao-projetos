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
        'a user called "{username}" '
        'with email "{email}" and password "{password}"'
    )
)
def create_user(session, context, username, email, password):
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
        'a team called "{team_name}" is created with user "{username}"'
    )
)
def create_team(client, context, team_name, username):
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
        'the user "{old_username}" changes their name to "{new_username}"'
    )
)
def update_user(client, context, old_username, new_username):
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
        'the team "{team_name}" must list "{expected_username}" as a member'
    )
)
def verify_member_of_the_team(client, context, team_name, expected_username):
    res = client.get('/teams/', headers=context['headers'])
    assert res.status_code == HTTPStatus.OK
    teams = res.json()

    # Encontra o time pelo nome
    time = next((t for t in teams if t['team_name'] == team_name), None)
    assert time is not None, f"Team '{team_name}' does not exist."

    membros = time['users']
    usernames = [m['username'] for m in membros]
    assert expected_username in usernames, (
        f"'{expected_username}' it's not one of the members: {usernames}"
    )
