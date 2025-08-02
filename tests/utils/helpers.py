from http import HTTPStatus

from conftest import TeamFactory, UserFactory
from utils.fake_data import (
    fake_project_name,
    fake_team_name,
    fake_user_data,
)

from task_flow.security import get_password_hash


def create_and_save_users(session, quantity=1):
    users = []
    for _ in range(quantity):
        data = fake_user_data()
        user = UserFactory(
            username=data['username'],
            email=data['email'],
            password=get_password_hash(data['password']),
        )
        session.add(user)
        users.append((user, data))
    session.commit()
    return users


def create_random_user_direct(session, context):
    users = create_and_save_users(session, quantity=1)
    user, data = users[0]

    context.update({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'password': data['password'],
    })
    return context


def update_user(client, user_id, user_data: dict, headers):
    return client.put(
        f'/users/{user_id}',
        json=user_data,
        headers=headers,
    )


def update_team(client, team_id, team_data: dict, headers):
    return client.patch(
        f'/teams/{team_id}',
        json=team_data,
        headers=headers,
    )


def find_team(client, headers, team_name):
    response = client.get(
        '/teams/', headers=headers, params={'team_name': team_name}
    )
    if response.status_code == HTTPStatus.NOT_FOUND:
        return None

    response.raise_for_status()

    teams = response.json()

    if not teams:
        return None

    return next(
        (team for team in teams if team['team_name'] == team_name), None
    )


def find_team_by_id(client, headers, team_id):
    response = client.get(f'/teams/{team_id}', headers=headers)
    if response.status_code == HTTPStatus.NOT_FOUND:
        return None
    response.raise_for_status()

    return response.json()


def add_user_to_team(client, team_id, team_name, users, headers):
    return client.patch(
        f'/teams/{team_id}',
        json={'team_name': team_name, 'user_list': users},
        headers=headers,
    )


def add_team_to_project(client, project_id, project_name, teams, headers):
    return client.patch(
        f'/projects/{project_id}',
        json={'project_name': project_name, 'team_list': teams},
        headers=headers,
    )


def authentication(client, context):
    # Autentica o usuário
    response = client.post(
        '/auth/token',
        data={'username': context['email'], 'password': context['password']},
    )
    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']
    context['headers'] = {'Authorization': f'Bearer {token}'}


def authenticate_user(client, email, password):
    # Autentica o segundo usuário
    response = client.post(
        '/auth/token',
        data={'username': email, 'password': password},
    )
    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def create_random_team_via_api(client, context, num_users=2):
    team_name = fake_team_name()
    context['team_name'] = team_name

    # Cria o time via api
    response = client.post(
        '/teams/',
        json={'team_name': team_name, 'user_list': [context['username']]},
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.CREATED, (
        f'Error while creating team: {response.json()}'
    )
    response_data = response.json()
    context['team_id'] = response_data['id']
    print('Team created:', team_name)


def create_random_team_direct(session, context, num_users=2):
    users_data = create_and_save_users(session, quantity=num_users)

    users = [user for user, _ in users_data]
    user_infos = [data for _, data in users_data]

    team_name = fake_team_name()
    team = TeamFactory(team_name=team_name, current_user_id=users[0].id)
    team.users.extend(users)
    session.add(team)
    session.commit()

    context['user_id'] = users[0].id
    context['username'] = user_infos[0]['username']
    context['email'] = user_infos[0]['email']
    context['password'] = user_infos[0]['password']

    context['team_id'] = team.id
    context['team_name'] = team.team_name
    return context


# criando um novo método devido a boa prática de responsabilidade única
def create_random_project_via_api(client, context):
    project_name = fake_project_name()
    context['project_name'] = project_name

    response = client.post(
        '/projects/',
        json={
            'project_name': project_name,
            'team_list': [context['team_name']],
        },
        headers=context['headers'],
    )

    assert response.status_code == HTTPStatus.CREATED, (
        f'Error while creating project: {response.json()}'
    )


def cannot_create_project_with_invalid_team(client, context):
    project_name = fake_project_name()
    context['project_name'] = project_name

    response = client.post(
        '/projects/',
        json={
            'project_name': project_name,
            'team_list': [context['team_name']],
        },
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'Expected not found status, got {response.status_code}: '
        f'{response.json()}'
    )
    expected_error = 'One or more teams do not exist'
    assert response.json()['detail'] == expected_error

    return response


def delete_updated_team(client, headers, team_id):
    response = client.delete(f'/teams/{team_id}', headers=headers)
    if response.status_code == HTTPStatus.NOT_FOUND:
        return None
    response.raise_for_status()
    return response.json() if response.content else None

def update_project(client, project_id, project_data: dict, headers):
    return client.patch(
        f'/projects/{project_id}', json=project_data, headers=headers
    )