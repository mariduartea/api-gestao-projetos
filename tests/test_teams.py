from http import HTTPStatus

from task_flow.utils.utils import (
    assert_team_has_users,
    get_team_by_id,
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


def test_not_read_teams_that_does_not_exist(client, token):
    response = client.get(
        '/teams',
        headers={'Authorization': f'Bearer {token}'},
        params={'team_name': 'newteam'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Team not found'}


def test_read_teams_with_id(client, token, team_with_users):
    response = client.get(
        f'/teams/{team_with_users.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data['id'] == team_with_users.id
    assert data['team_name'] == team_with_users.team_name


def test_not_read_teams_with_id_greater_than_length(
    client, token, team_with_users
):
    valid_id = team_with_users.id
    invalid_id = valid_id + 1

    response = client.get(
        f'/teams/{invalid_id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Team not found'}


def test_not_read_teams_with_id_less_than_1(client, token):
    invalid_id = 0
    response = client.get(
        f'/teams/{invalid_id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Team not found'}


# atualizar o nome do time com sucesso
def test_update_team_name(client, owner_token, team_with_users, users):
    response = client.patch(
        f'/teams/{team_with_users.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={'team_name': 'newTeamName'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == team_with_users.id
    assert data['team_name'] == 'newTeamName'
    assert_team_has_users(data, users)


# atualizar um time cujo id não existe
# com id +1
def test_not_update_teams_with_id_greater_than_length(
    client, owner_token, team_with_users, users
):
    valid_id = team_with_users.id
    invalid_id = valid_id + 1
    response = client.patch(
        f'/teams/{invalid_id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={
            'team_name': 'newTeamName',
            'user_list': [user.username for user in users],
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Team not found'}


# atualizar um time cujo id não existe
# com id = 0
def test_not_update_teams_with_id_less_than_1(client, token, users):
    invalid_id = 0
    response = client.patch(
        f'/teams/{invalid_id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'team_name': 'newTeamName',
            'user_list': [user.username for user in users],
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Team not found'}


# atualizar o nome do time com um que ja existe
def test_not_update_team_name_with_already_existed_name(
    client, owner_token, team_with_users, another_team_with_same_name
):
    response = client.patch(
        f'/teams/{team_with_users.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={'team_name': another_team_with_same_name.team_name},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Team name alreaty exists'}


# atualizar time adicionando um novo usuário
def test_update_team_user_list_adding_a_new_user(
    client, owner_token, team_with_users, users, other_user
):
    response = client.patch(
        f'/teams/{team_with_users.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={
            'user_list': [user.username for user in users]
            + [other_user.username],
        },
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == team_with_users.id
    # Valide que todos os usuários (antigos + novo) estão no time
    returned_usernames = {u['username'] for u in data['users']}
    expected_usernames = {user.username for user in users} | {
        other_user.username
    }
    assert returned_usernames == expected_usernames


# atualizar time removendo um novo usuário
def test_update_team_user_list_removing_a_user(
    client, owner_token, team_with_users, users
):
    # Remove o primeiro usuário da lista
    removed_user = users[0]
    remaining_users = users[1:]

    response = client.patch(
        f'/teams/{team_with_users.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={'user_list': [user.username for user in remaining_users]},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == team_with_users.id

    returned_usernames = {u['username'] for u in data['users']}
    expected_usernames = {user.username for user in remaining_users}
    assert returned_usernames == expected_usernames
    assert removed_user.username not in returned_usernames


# atualizar os usuarios:
# adicionar um usuario que nao existe detail='Users not found',
def test_not_update_team_with_non_existent_user(
    client, owner_token, team_with_users, users
):
    response = client.patch(
        f'/teams/{team_with_users.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={
            'user_list': [user.username for user in users] + ['newUser'],
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Users not found'}


# deixar a lista de usuarios vazia
def test_not_update_teams_without_users(client, owner_token, team_with_users):
    response = client.patch(
        f'/teams/{team_with_users.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={
            'user_list': [],
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Team must have at least one user'}


# teste para validar que nao pode alterar um time de outro usuário
def test_cannot_update_team_of_another_user(
    client, another_owner_token, team_with_users
):
    response = client.patch(
        f'/teams/{team_with_users.id}',
        headers={'Authorization': f'Bearer {another_owner_token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()['detail'].startswith(
        'You are not allowed to update this team. '
        'Only the team owner can perform this action.'
    )


# deletar time com sucesso
def test_delete_team_successfully(client, owner_token, team_with_users):
    response = client.delete(
        f'/teams/{team_with_users.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Team deleted successfully'}


def test_not_delete_teams_with_id_greater_than_length(
    client, token, team_with_users
):
    valid_id = team_with_users.id
    invalid_id = valid_id + 1

    response = client.delete(
        f'/teams/{invalid_id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Team not found'}


# atualizar um time cujo id não existe
# com id = 0
def test_not_delete_teams_with_id_less_than_1(client, token, users):
    invalid_id = 0
    response = client.delete(
        f'/teams/{invalid_id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Team not found'}


# teste para validar que nao pode deletar um time de outro usuário
def test_cannot_delete_team_of_another_user(
    client, another_owner_token, team_with_users
):
    response = client.delete(
        f'/teams/{team_with_users.id}',
        headers={'Authorization': f'Bearer {another_owner_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()['detail'].startswith(
        'You are not allowed to delete this team. '
        'Only the team owner can perform this action.'
    )
