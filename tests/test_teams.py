from http import HTTPStatus


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


def test_not_create_team_with_users_do_not_exist(client, token):
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
            'user_list': [user.username]
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Team already created'}
