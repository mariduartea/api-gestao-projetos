from http import HTTPStatus


# TESTES DE CRIAR PROJETOS #################
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
