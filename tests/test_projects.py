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
