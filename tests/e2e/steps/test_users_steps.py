from http import HTTPStatus

import pytest
from conftest import UserFactory
from pytest_bdd import given, scenarios, then, when
from utils.fake_data import fake_team_name, fake_user_data, fake_project_name

from task_flow.security import get_password_hash

scenarios('../feature/users.feature')


@pytest.fixture
def context():
    return {}


# Scenario: Update a user and verify that the change appears in the team list
@given('a random user is created')
def create_user(session, context):
    data = fake_user_data()
    user = UserFactory(
        username=data['username'],
        email=data['email'],
        password=get_password_hash(data['password']),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    context['user_id'] = user.id
    context['username'] = data['username']
    context['email'] = data['email']
    context['password'] = data['password']
    print('👤 User created:', data['username'])


@given('a random team is created with that user')
def create_team(client, context):
    #Autentica o usuário
    response = client.post(
        '/auth/token',
        data={'username': context['email'], 'password': context['password']},
    )
    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']
    context['headers'] = {'Authorization': f'Bearer {token}'}

    #Gera nome do time
    team_name = fake_team_name()
    context['team_name'] = team_name

    #Cria o time via api
    response = client.post(
        '/teams/',
        json={'team_name': team_name, 'user_list': [context['username']]},
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.CREATED, (
        f'Error while creating team: {response.json()}'
    )
    print('🛡️ Team created:', team_name)


@when('the user changes their name')
def update_user(client, context):
    new_username = f"super{context['username']}"
    response = client.put(
        f'/users/{context["user_id"]}',
        json={
            'username': new_username,
            'email': context['email'],
            'password': context['password'],
        },
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.OK, 'Error while update user'
    context['username'] = new_username


@then('the team must list the new name as a member')
def verify_member_of_the_team(client, context):
    response = client.get('/teams/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK
    teams = response.json()

    team_name = context['team_name']
    #Encontra o time pelo nome
    time = next((t for t in teams if t['team_name'] == team_name), None)
    assert time is not None, f"Team '{context['team_name']}' does not exist."

    membros = time['users']
    usernames = [m['username'] for m in membros]
    assert context['username'] in usernames, (
        f"'{context['username']}' it's not one of the members: {usernames}"
    )

# Scenario: Update a user and verify that the change appears in the project list
@given('a random user is created')
def create_user(session, context):
    data = fake_user_data()
    user = UserFactory(
        username=data['username'],
        email=data['email'],
        password=get_password_hash(data['password']),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    context['user_id'] = user.id
    context['username'] = data['username']
    context['email'] = data['email']
    context['password'] = data['password']
    print('👤 User created:', data['username'])


@given('a random team is created with that user')
def create_team(client, context):
    #Autentica o usuário
    response = client.post(
        '/auth/token',
        data={'username': context['email'], 'password': context['password']},
    )
    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']
    context['headers'] = {'Authorization': f'Bearer {token}'}

    #Gera nome do time
    team_name = fake_team_name()
    context['team_name'] = team_name

    #Cria o time via api
    response = client.post(
        '/teams/',
        json={'team_name': team_name, 'user_list': [context['username']]},
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.CREATED, (
        f'Error while creating team: {response.json()}'
    )
    print('🛡️ Team created:', team_name)

@given('a random project is created with that team')
def create_project(client, context):
    project_name = fake_project_name()
    context['project_name'] = project_name

    response = client.post(
        '/projects/',
        json={'project_name': project_name, 'team_list': [context['team_name']]},
        headers=context['headers'])

    assert response.status_code == HTTPStatus.CREATED, (
        f"Error while creating project: {response.json()}"
    )


@when('the user changes their name')
def update_username(client, context):
    new_username = f"super{context['username']}"

    response = client.put(
        f"/users/{context['user_id']}",
        headers=context['headers'],
        json={'username': new_username,
              'email': context['email'],
              'password': context['password']}
    )

    assert response.status_code == HTTPStatus.OK
    context['username'] = new_username


@then('the project must list the new name as a member')
def verify_member_of_the_team(client, context):
    response = client.get('/projects/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK

    projects = response.json()

    #Encontra o projeto pelo nome
    project = next((t for t in projects if
      t['project_name'] == context['project_name']), None)
    assert project is not None, f"Project '{context['project_name']}' does not exist."

    print("🔎 project response:", project)

    usernames = []
    for team in project["teams"]:
        for user in team["users"]:
            usernames.append(user["username"])

    assert context['username'] in usernames, (
        f"'{context['username']}' it's not one of the members: {usernames}"
    )
