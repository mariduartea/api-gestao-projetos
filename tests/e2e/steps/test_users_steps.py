from http import HTTPStatus

import pytest
from pytest_bdd import given, scenarios, then, when
from utils.helpers import (
    add_user_to_team,
    authenticate_user,
    authentication,
    create_random_project,
    create_random_team,
    create_random_user,
    update_user,
)

scenarios('../feature/users.feature')


@pytest.fixture
def context():
    return {}


# CT001
@given('a random user is created')
def random_user_is_created(session, context):
    create_random_user(session, context)


@when('the user changes their name and email')
def user_changes_name_and_email(client, context):
    authentication(client, context)
    new_username = f'super{context["username"]}'
    new_email = f'{new_username}@cidadeville.com'

    response = update_user(
        client=client,
        user_id=context['user_id'],
        user_data={
            'username': new_username,
            'email': new_email,
            'password': context['password'],
        },
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.OK, (
        'Error while update username or email'
    )
    context['username'] = new_username
    context['email'] = new_email


@then('the user list must reflect the updated user')
def verify_user_list_updates(client, context):
    response = client.get('/users/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK

    users = response.json()['users']
    user = next(
        (
            u
            for u in users
            if u['username'] == context['username']
            and u['email'] == context['email']
        ),
        None,
    )

    assert user is not None, 'Updated user not found in user list'


# CT002
@given('a random team is created with that user')
def random_team_is_created(client, context):
    authentication(client, context)
    create_random_team(client, context)


@when('the user changes their name')
def user_changes_name(client, context):
    new_username = f'super{context["username"]}'
    response = update_user(
        client=client,
        user_id=context['user_id'],
        user_data={
            'username': new_username,
            'email': context['email'],
            'password': context['password'],
        },
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.OK, 'Error while update username'
    context['username'] = new_username


@then('the team must list the new name as a member')
def verify_member_of_the_team(client, context):
    response = client.get('/teams/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK

    teams = response.json()
    team_name = context['team_name']
    # Encontra o time pelo nome
    team = next((t for t in teams if t['team_name'] == team_name), None)
    assert team is not None, f"Team '{context['team_name']}' does not exist."

    membros = team['users']
    usernames = [m['username'] for m in membros]
    assert context['username'] in usernames, (
        f"'{context['username']}' it's not one of the members: {usernames}"
    )


# CT003
@given('a random project is created with that team')
def random_project_is_created(client, context):
    create_random_project(client, context)


@then('the project must list the new name as a member')
def verify_member_of_the_project(client, context):
    response = client.get('/projects/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK

    projects = response.json()
    project = next(
        (t for t in projects if t['project_name'] == context['project_name']),
        None,
    )
    assert project is not None, (
        f"Project '{context['project_name']}' does not exist."
    )

    usernames = []
    for team in project['teams']:
        for user in team['users']:
            usernames.append(user['username'])

    assert context['username'] in usernames, (
        f"'{context['username']}' it's not one of the members: {usernames}"
    )


# CT004
@given('another random user is created')
def another_random_user_is_created(session, context):
    another_context = {}
    another_user = create_random_user(session, another_context)
    context['another_user'] = another_user


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

    response = add_user_to_team(
        client,
        context['team_id'],
        context['team_name'],
        user_list,
        context['headers'],
    )
    assert response.status_code == HTTPStatus.OK, 'user not found'


@when('the other user is deleted')
def delete_user_from_system(client, context):
    # autenticar com o usuário criado
    second_user = context['another_user']

    headers = authenticate_user(
        client, second_user['email'], second_user['password']
    )

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


# CT005
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

    response = add_user_to_team(
        client,
        context['team_id'],
        context['team_name'],
        user_list,
        context['headers'],
    )

    assert response.status_code == HTTPStatus.OK


@given('a random project is created with that updated team')
def step_create_second_project(client, context):
    create_random_project(client, context)


@when('the third user is deleted')
def delete_third_user_from_system(client, context):
    # autenticar com o usuário criado
    third_user = context['third_user']

    headers = authenticate_user(
        client, third_user['email'], third_user['password']
    )

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


# CT006
@given('a new user is created')
def creating_user_to_be_deleted(session, context):
    new_context = {}
    user_to_be_deleted = create_random_user(session, new_context)
    context['user_to_be_deleted'] = user_to_be_deleted


@when('the new user is deleted')
def deleting_user(client, context):
    user = context['user_to_be_deleted']
    headers = authenticate_user(client, user['email'], user['password'])

    response = client.delete(f'/users/{user["user_id"]}', headers=headers)
    assert response.status_code == HTTPStatus.OK

    context['deleted_user_id'] = user['user_id']


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
            'user_list': [context['user_to_be_deleted']['username']],
        },
        headers=context['headers'],
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'One or more users do not exist'
