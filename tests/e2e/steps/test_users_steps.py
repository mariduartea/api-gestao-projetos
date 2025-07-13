from http import HTTPStatus

import pytest
from pytest_bdd import given, scenarios, then, when
from utils.helpers import (
    authentication,
    create_random_project_via_api,
    create_random_team_via_api,
    create_random_user_direct,
)

scenarios('../features/users.feature')


@pytest.fixture
def context():
    return {}


# Scenario: Update a user and verify that the change appears in the team list
@given('a random user is created')
def step_create_user(session, context):
    data = create_random_user_direct(session, context)
    context.update(data)


@given('a random team is created with that user')
def step_create_team(client, context):
    authentication(client, context)
    create_random_team_via_api(client, context)


@when('the user changes their name')
def update_user_name(client, context):
    new_username = f'super{context["username"]}'
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
        'Error while update user name'
    )
    context['username'] = new_username


@then('the team must list the new name as a member')
def verify_member_of_the_team(client, context):
    response = client.get('/teams/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK
    teams = response.json()

    team_name = context['team_name']
    # Encontra o time pelo nome
    time = next((t for t in teams if t['team_name'] == team_name), None)
    assert time is not None, f"Team '{context['team_name']}' does not exist."

    membros = time['users']
    usernames = [m['username'] for m in membros]
    assert context['username'] in usernames, (
        f"'{context['username']}' it's not one of the members: {usernames}"
    )


# Scenario: Updt a user and verify that the change appears in the project list
@given('a random project is created with that team')
def step_create_project(client, context):
    create_random_project_via_api(client, context)


@when('the user changes their name')
def update_username(client, context):
    new_username = f'super{context["username"]}'

    response = client.put(
        f'/users/{context["user_id"]}',
        headers=context['headers'],
        json={
            'username': new_username,
            'email': context['email'],
            'password': context['password'],
        },
    )

    assert response.status_code == HTTPStatus.OK
    context['username'] = new_username


@then('the project must list the new name as a member')
def verify_member_of_the_project(client, context):
    response = client.get('/projects/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK

    projects = response.json()

    # Encontra o projeto pelo nome
    project = next(
        (t for t in projects if t['project_name'] == context['project_name']),
        None,
    )
    assert project is not None, (
        f"Project '{context['project_name']}' does not exist."
    )

    print('🔎 project response:', project)

    usernames = []
    for team in project['teams']:
        for user in team['users']:
            usernames.append(user['username'])

    assert context['username'] in usernames, (
        f"'{context['username']}' it's not one of the members: {usernames}"
    )


# Scenario: Del a user and ver that they no long appear as a member of a team
@given('another random user is created')
def create_another_user(session, context):
    another_context = {}
    another_user = create_random_user_direct(session, another_context)
    context['second_user'] = another_user

@given('the team list is updated with the new user')
def update_the_team_list(client, context):
    # autentica com o usuário que criou o time
    authentication(client, context)

    # busca os dados do time
    response = client.get('/teams/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK

    teams = response.json()
    team = next(
        (t for t in teams if t['team_name'] == context['team_name']), None
    )
    assert team is not None

    team_id = team['id']
    context['team_id'] = team_id

    # adiciona o novo usuário à lista de usuários
    user_list = [user['username'] for user in team['users']]
    user_list.append(context['another_user']['username'])

    response = client.patch(
        f'/teams/{context["team_id"]}',
        json={'team_name': context['team_name'], 'user_list': user_list},
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.OK


@when('the other user is deleted')
def delete_user_from_system(client, context):
    # autenticar com o usuário criado
    second_user = context['another_user']

    response = client.post(
        '/auth/token',
        data={
            'username': second_user['email'],
            'password': second_user['password'],
        },
    )
    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    response = client.delete(
        f'/users/{second_user["user_id"]}', headers=headers
    )
    assert response.status_code == HTTPStatus.OK


@then('the team must not list the deleted user as a member')
def verify_deleted_member_of_the_team(client, context):
    # reautenticar com o usuario que criou o time
    authentication(client, context)

    response = client.get('/teams/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK

    team = next(
        (t for t in response.json() if t['team_name'] == context['team_name']),
        None,
    )
    assert team is not None

    usernames = [m['username'] for m in team['users']]

    assert context['another_user']['username'] not in usernames, (
        f"User '{context['another_user']}' was not deleted "
        f'from team members: {usernames}'
    )


# Scenario: Del a user and ver that they no long appear as a member
@given('another third random user is created')
def create_third_random_user(session, context):
    second_context = {}
    third_user = create_random_user(session, second_context)
    context['third_user'] = third_user


@given('the team list is updated with the third user')
def new_update_for_team_list(client, context):
    # autentica com o usuário que criou o time
    authentication(client, context)

    # busca os dados do time
    response = client.get('/teams/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK

    teams = response.json()
    team = next(
        (t for t in teams if t['team_name'] == context['team_name']), None
    )
    assert team is not None

    team_id = team['id']
    context['team_id'] = team_id

    # adiciona o novo usuário à lista de usuários
    user_list = [user['username'] for user in team['users']]
    user_list.append(context['third_user']['username'])

    response = client.patch(
        f'/teams/{context["team_id"]}',
        json={'team_name': context['team_name'], 'user_list': user_list},
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.OK
    print('lista de time atualizada:', user_list)


@given('a random project is created with that updated team')
def step_create_second_project(client, context):
    create_random_project(client, context)


@when('the third user is deleted')
def delete_third_user_from_system(client, context):
    # autenticar com o usuário criado
    third_user = context['third_user']

    response = client.post(
        '/auth/token',
        data={
            'username': third_user['email'],
            'password': third_user['password'],
        },
    )
    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # delete o usuário
    response = client.delete(
        f'/users/{third_user["user_id"]}', headers=headers
    )
    assert response.status_code == HTTPStatus.OK


@then('the project must not list the deleted user as a member')
def verify_deleted_member_in_the_project(client, context):
    # reautenticar com o usuario que criou o time
    authentication(client, context)

    response = client.get('/projects/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK

    project = next(
        (
            t
            for t in response.json()
            if t['project_name'] == context['project_name']
        ),
        None,
    )
    assert project is not None

    usernames = []
    for team in project['teams']:
        for user in team['users']:
            usernames.append(user['username'])

    assert context['third_user']['username'] not in usernames, (
        f"User '{context['third_user']}' was not deleted "
        f'from project members: {usernames}'
    )


# Scenario: Del a user and attempt to create a team with that user
@given('a new user is created')
def create_new_user(session, context):
    new_context = {}
    new_user = create_random_user(session, new_context)
    context['new_user'] = new_user


@when('the new user is deleted')
def delete_new_user(client, context):
    new_user = context['new_user']

    response = client.post(
        '/auth/token',
        data={
            'username': new_user['email'],
            'password': new_user['password'],
        },
    )
    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    new_user_id = context['new_user']['user_id']
    context['new_user_id'] = new_user_id

    response = client.delete(
        f'/users/{context["new_user_id"]}', headers=headers
    )
    assert response.status_code == HTTPStatus.OK


@then(
    'creating a team with the deleted user should return the error '
    '"One or more users do not exist"'
)
def create_team_with_deleted_user(client, context):
    authentication(client, context)
    response = client.post(
        '/teams/',
        json={
            'team_name': 'team_with_error',
            'user_list': [context['new_user']['username']],
        },
        headers=context['headers'],
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'One or more users do not exist'
