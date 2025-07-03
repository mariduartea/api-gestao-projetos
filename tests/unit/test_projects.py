from http import HTTPStatus

from task_flow.utils.utils import assert_project_has_teams, get_project_by_id


# >>>>>> TESTES DE CRIAR PROJETOS
def test_create_projects(client, team_list, token):
    response = client.post(
        '/projects',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'project_name': 'meu_projeto_teste',
            'team_list': [team.team_name for team in team_list],
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['project_name'] == 'meu_projeto_teste'
    # teams como resposta da API e team_list como os times do teste
    assert len(data['teams']) == len(team_list)


def test_not_create_project_with_teams_does_not_exist(client, token):
    response = client.post(
        '/projects',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'project_name': 'meu_projeto_teste',
            'team_list': ['aaaaaaaaaaaa', 'eeeeeeeee'],
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'One or more teams do not exist'}


def test_not_create_team_that_already_exist(
    client, token, projects_with_teams, team_list
):
    response = client.post(
        '/projects',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'project_name': projects_with_teams.project_name,
            'team_list': [team.team_name for team in team_list],
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Project already created'}


# >>>>>> TESTES DE LER PROJETOS
def test_read_projects(client, token, projects_with_teams, team_list):
    response = client.get(
        '/projects',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    project = get_project_by_id(data, projects_with_teams.id)
    assert project is not None
    assert project['project_name'] == projects_with_teams.project_name
    assert_project_has_teams(project, team_list)


# Ler projeto pelo nome
def test_read_project_with_name(client, token, projects_with_teams, team_list):
    response = client.get(
        # f'/projects/?project_name={projects_with_teams.project_name}',
        '/projects',
        headers={'Authorization': f'Bearer {token}'},
        params={'project_name': projects_with_teams.project_name},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # dicionario
    assert data[0]['id'] == projects_with_teams.id
    assert data[0]['project_name'] == projects_with_teams.project_name


# Ler projeto pelo nome errado
def test_not_read_project_that_does_not_exist(client, token):
    response = client.get(
        '/projects',
        headers={'Authorization': f'Bearer {token}'},
        params={'project_name': 'newproject'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Project not found'}


def test_read_project_with_id(client, token, projects_with_teams, team_list):
    response = client.get(
        f'/projects/{projects_with_teams.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == projects_with_teams.id
    assert data['project_name'] == projects_with_teams.project_name


def test_not_read_project_with_id_greater_than_length(
    client, token, projects_with_teams, team_list
):
    invalid_id = projects_with_teams.id + 1
    response = client.get(
        f'/projects/{invalid_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Project not found'}


def test_not_read_project_with_id_less_than_1(
    client, token, projects_with_teams, team_list
):
    invalid_id = 0
    response = client.get(
        f'/projects/{invalid_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Project not found'}


# >>>>>> TESTES DE ATUALIZAR PROJETOS


# atualizar o nome do projeto com sucesso
def test_update_project_name(
    client, owner_token, projects_with_teams, team_list
):
    response = client.patch(
        f'/projects/{projects_with_teams.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={'project_name': 'newProjectName'},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['project_name'] == 'newProjectName'
    assert data['id'] == projects_with_teams.id
    assert_project_has_teams(data, team_list)


# atualizar um projeto cujo id não existe
# com id +1
def test_not_update_project_with_id_greater_than_length(
    client, owner_token, projects_with_teams, team_list
):
    invalid_id = projects_with_teams.id + 1
    response = client.patch(
        f'/projects/{invalid_id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={
            'project_name': 'newProjectName',
            'team_list': [team.team_name for team in team_list],
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Project not found'}


# atualizar um projeto cujo id não existe
# com id = 0
def test_not_update_project_with_id_greater_than_1(
    client, owner_token, projects_with_teams, team_list
):
    invalid_id = 0
    response = client.patch(
        f'/projects/{invalid_id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={
            'project_name': 'newProjectName',
            'team_list': [team.team_name for team in team_list],
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Project not found'}


# atualizar o nome do projeto com um que ja existe
def test_not_update_project_with_already_existed_name(
    client, owner_token, projects_with_teams, another_project_with_same_name
):
    response = client.patch(
        f'/projects/{projects_with_teams.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={'project_name': another_project_with_same_name.project_name},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Project name already exists'}


# atualizar projeto adicionando um novo time
def test_update_project_list_adding_a_new_team(
    client, owner_token, projects_with_teams, team_list, other_team_list
):
    response = client.patch(
        f'/projects/{projects_with_teams.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={
            'team_list': [team.team_name for team in team_list]
            + [other_team.team_name for other_team in other_team_list],
        },
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == projects_with_teams.id
    returned_team_names = {t['team_name'] for t in data['teams']}
    expected_team_names = {team_list.team_name for team_list in team_list} | {
        other_team_list.team_name for other_team_list in other_team_list
    }
    assert returned_team_names == expected_team_names


# atualizar projeto removendo um time
def test_update_project_list_removing_a_team(
    client, owner_token, projects_with_teams, team_list
):
    # Remove o primeiro time da lista
    removed_team = team_list[0]
    remaining_teams = team_list[1:]

    response = client.patch(
        f'/projects/{projects_with_teams.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={'team_list': [team.team_name for team in remaining_teams]},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == projects_with_teams.id
    returned_team_names = {t['team_name'] for t in data['teams']}
    expected_team_names = {
        team_list.team_name for team_list in remaining_teams
    }
    assert returned_team_names == expected_team_names
    assert removed_team.team_name not in returned_team_names


# adicionar um time que nao existe
def test_not_update_project_with_non_existent_team(
    client, owner_token, projects_with_teams, team_list
):
    response = client.patch(
        f'/projects/{projects_with_teams.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={
            'team_list': [team.team_name for team in team_list]
            + ['nonExistentTeam'],
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Teams not found'}


# deixar a lista de times vazia
def test_not_update_project_without_teams(
    client, owner_token, projects_with_teams, team_list
):
    response = client.patch(
        f'/projects/{projects_with_teams.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={'team_list': []},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Project must have at least one team'}


# teste para validar que nao pode alterar um projeto de outro usuario
def test_not_update_another_user_project(
    client, another_owner_token, projects_with_teams
):
    response = client.patch(
        f'/projects/{projects_with_teams.id}',
        headers={'Authorization': f'Bearer {another_owner_token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()['detail'].startswith(
        'You are not allowed to update this project. '
        'Only the team owner can perform this action.'
    )


# >>>>>> TESTES DE DELETAR PROJETOS


# deletar projeto com sucesso
def test_delete_project_successfully(client, owner_token, projects_with_teams):
    response = client.delete(
        f'/projects/{projects_with_teams.id}',
        headers={'Authorization': f'Bearer {owner_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Project deleted successfully'}


# não deletar com um id que não existe (id maior que a quantidade de projetos)
def test_not_delete_project_with_id_greater_than_length(
    client, token, projects_with_teams
):
    invalid_id = projects_with_teams.id + 1
    response = client.delete(
        f'/projects/{invalid_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Project not found'}


# não deletar com um id que não existe (id = 0)
def test_not_delete_project_with_id_less_than_1(
        client, token, projects_with_teams
):
    invalid_id = 0
    response = client.delete(
        f'/projects/{invalid_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Project not found'}


def test_not_delete_another_user_project(
        client, another_owner_token, projects_with_teams
):
    response = client.delete(
        f'/projects/{projects_with_teams.id}',
        headers={'Authorization': f'Bearer {another_owner_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()['detail'].startswith(
        'You are not allowed to delete this project. '
        'Only the project owner can perform this action.'
    )
