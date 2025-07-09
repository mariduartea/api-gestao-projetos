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
    response = client.post(
        '/auth/token',
        data={'username': context['email'], 'password': context['password']},
    )
    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']
    context['headers'] = {'Authorization': f'Bearer {token}'}
    context['team_name'] = team_name

    # Cria o time via API
    response = client.post(
        '/teams/',
        json={'team_name': team_name, 'user_list': [username]},
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.CREATED, (
        f"Error while creating team: {response.json()}"
)


@when(
    parsers.parse(
        'the user "{old_username}" changes their name to "{new_username}"'
    )
)
def update_user(client, context, old_username, new_username):
    response = client.put(
        f'/users/{context["user_id"]}',
        json={
            'username': new_username,
            'email': context['email'],
            'password': context['password'],
        },
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.OK, (
        "Error while update user"
    )
    context['username'] = new_username


@then(
    parsers.parse(
        'the team "{team_name}" must list "{expected_username}" as a member'
    )
)
def verify_member_of_the_team(client, context, team_name, expected_username):
    response = client.get('/teams/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK
    teams = response.json()

    # Encontra o time pelo nome
    time = next((t for t in teams if t['team_name'] == team_name), None)
    assert time is not None, f"Team '{team_name}' does not exist."

    membros = time['users']
    usernames = [m['username'] for m in membros]
    assert expected_username in usernames, (
        f"'{expected_username}' it's not one of the members: {usernames}"
    )


@given(
    parsers.parse(
        'a project called "{project_name}" is created with team "{team_name}"'
    )
)
def create_project(client, project_name, team_name, context):
    response = client.post(
        '/projects/',
        json={'project_name': project_name, 'team_list': [team_name]},
        headers=context['headers'])

    assert response.status_code == HTTPStatus.CREATED, (
        f"Error while creating project: {response.json()}"
    )
    context['project_name'] = project_name


@when(
    parsers.parse(
        'the user "{old_username}" changes their name to "{expected_username}"'
    )
)
def update_username(client, old_username, new_username, context):
    response = client.put(
        f"/users/{context['user_id']}",
        headers=context['headers'],
        json={'username': new_username,
              'email': context['email'],
              'password': context['password']}
    )

    assert response.status_code == HTTPStatus.OK
    context['username'] = new_username


@then(
    parsers.parse(
        'the project "{project_name}" must list "{expected_username}" as a member'
    )
)
def verify_member_of_the_team(client, context, project_name, expected_username):
    response = client.get('/projects/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK

    projects = response.json()

    # Encontra o projeto pelo nome
    project = next((t for t in projects if t['project_name'] == project_name), None)
    assert project is not None, f"Project '{project_name}' does not exist."

    print("🔎 project response:", project)

    usernames = []
    for team in project["teams"]:
        for user in team["users"]:
            usernames.append(user["username"])

    assert expected_username in usernames, (
        f"'{expected_username}' it's not one of the members: {usernames}"
    )
