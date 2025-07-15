from http import HTTPStatus

from conftest import UserFactory
from utils.fake_data import fake_project_name, fake_team_name, fake_user_data

from task_flow.security import get_password_hash


def create_random_user(session, context):
    data = fake_user_data()
    user = UserFactory(
        username=data['username'],
        email=data['email'],
        password=get_password_hash(data['password']),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    context.update({
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "password": data["password"],
    })
    return context

def update_user(client, user_id, username, email, password, headers):
    return client.put(
        f'/users/{user_id}',
        json={'username': username, 'email': email, 'password': password},
        headers=headers,
    )

def add_user_to_team(client, team_id, team_name, users, headers):
    return client.patch(
        f'/teams/{team_id}',
        json={'team_name': team_name, 'user_list': users},
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
    # Autentica o usuário
    response = client.post(
        '/auth/token',
        data={'username': email, 'password': password},
    )
    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}

def create_random_team(client, context):
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


def create_random_project(client, context):
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
