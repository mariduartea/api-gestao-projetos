from http import HTTPStatus

from task_flow.utils.utils import (
    assert_team_has_users,
    get_team_by_id,
    get_team_count,
)


def test_create_teams(client, token):
    # 1. Criação dos usuários necessários
    users_to_create = [
        {
            'username': 'mari',
            'email': 'mari@email.com',
            'password': 'bolinha123',
        },
        {
            'username': 'bia',
            'email': 'bia@email.com',
            'password': 'bolinha123',
        },
    ]
    for user in users_to_create:
        client.post('/users', json=user)

    usernames = [user['username'] for user in users_to_create]

    # 2. Criação do time com esses usuários
    team_data = {'team_name': 'bolinha', 'user_list': usernames}

    response = client.post(
        '/teams', headers={'Authorization': f'Bearer {token}'}, json=team_data
    )

    # 3. Validações
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    user_count = 2
    assert data['team_name'] == 'bolinha'
    assert len(data['users']) == user_count

    usernames = {u['username'] for u in data['users']}
    assert usernames == {'mari', 'bia'}
    emails = {u['email'] for u in data['users']}
    assert emails == {'mari@email.com', 'bia@email.com'}


def test_not_create_team_with_users_does_not_exist(client, token):
    response = client.post(
        '/teams',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'team_name': 'bolinha',
            'user_list': ['lele', 'lala'],
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'One or more users do not exist'}


def test_not_create_team_that_already_exist(
    client, team_with_users, user, token
):
    response = client.post(
        '/teams',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'team_name': team_with_users.team_name,
            'user_list': [user.username],
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Team already created'}


def test_read_teams(client, token, team_with_users, users):
    response = client.get(
        '/teams',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    team = get_team_by_id(data, team_with_users.id)
    assert team is not None
    assert team['team_name'] == team_with_users.team_name
    assert_team_has_users(team, users)


def test_read_teams_that_does_not_exist(client, token):
    response = client.get(
        '/teams',
        headers={'Authorization': f'Bearer {token}'},
        params={'team_name': 'newteam'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Team does not exist'}


def test_read_teams_with_id(client, token, team_with_users):
    response = client.get(
        f'/teams/{team_with_users.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data['id'] == team_with_users.id
    assert data['team_name'] == team_with_users.team_name


def test_read_teams_with_id_that_does_not_exist(client, token, session):
    invalid_id = get_team_count(session) + 1
    response = client.get(
        f'/teams/{invalid_id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Team does not exist'}
