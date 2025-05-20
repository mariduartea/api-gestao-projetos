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
