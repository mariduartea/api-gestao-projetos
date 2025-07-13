from http import HTTPStatus

from conftest import UserFactory, TeamFactory
from utils.fake_data import fake_project_name, fake_team_data, fake_team_name, fake_user_data

from task_flow.security import get_password_hash

def create_and_save_users(session, quantity=1):
    users = []
    for _ in range(quantity):
        data = fake_user_data()
        user = UserFactory(
            username = data['username'],
            email = data['email'],
            password = get_password_hash(data['password'])
        )
        session.add(user)
        users.append((user, data))
    session.commit()
    return users

def create_random_user_direct(session, context):
    users = create_and_save_users(session, quantity=1)
    user, data = users[0]

    context['user_id'] = user.id
    context['username'] = data['username']
    context['email'] = data['email']
    context['password'] = data['password']
    print('User created:', data['username'])
    return context


def authentication(client, context):
    # Autentica o usuário
    response = client.post(
        '/auth/token',
        data={'username': context['email'], 'password': context['password']},
    )
    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']
    context['headers'] = {'Authorization': f'Bearer {token}'}

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
    context["team_id"] = response_data["id"]
    print('Team created:', team_name)

def create_random_team_direct(session, context, num_users=2):
    users_data = create_and_save_users(session, quantity=num_users)

    users = [user for user, _ in users_data]
    user_infos = [data for _, data in users_data]

    team_name = fake_team_name()
    team = TeamFactory(
        team_name=team_name,
        users=users
    )
    session.add(team)
    session.commit()

    context['user_id'] = users[0].id
    context['username'] = user_infos[0]['username']
    context['email'] = user_infos[0]['email']
    context['password'] = user_infos[0]['password']

    context['team_id'] = team.id
    context['team_name'] = team.team_name
    return context


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
