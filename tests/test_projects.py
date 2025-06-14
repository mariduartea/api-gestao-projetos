from http import HTTPStatus


def test_create_projects(client, projects_with_teams, team_list, token):
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
