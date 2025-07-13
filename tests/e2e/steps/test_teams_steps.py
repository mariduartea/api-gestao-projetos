from http import HTTPStatus

import pytest
from pytest_bdd import given, scenarios, then, when
from utils.helpers import (
    authentication,
    create_random_user_direct,
    create_random_team_via_api,
    create_random_project_via_api,
)

scenarios('../features/teams.feature')

@pytest.fixture
def context():
    return {}

# Scenario: Update a team and verify that the changes appear in the project list
@given("the API has a registered team")
def verify_registered_team(session, client, context):
    create_random_user_direct(session, context)
    authentication(client, context)
    data = create_random_team_via_api(client, context)
    # context.update(data)

@given("this team is associated with a project")
def verify_associated_team_with_project(client, context):
    create_random_project_via_api(client, context)

@when("this team is edited")
def edit_team(client, context):
    new_team_name = f'Updated {context["team_name"]}'
    response = client.patch(
        f'/teams/{context["team_id"]}',
        json={'team_name': new_team_name},
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.OK, (
        f'Error while updating team: {response.json()}'
    )
    # Atualiza o context com o novo nome
    context['team_name'] = new_team_name
    
@then("the updates should be reflected in the project")
def verify_updated_team_in_project(client, context):
    response = client.get('/projects/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK, (
        f'Error while fetching projects: {response.json()}'
    )
    projects = response.json()
    project_name = context['project_name']
    # Com o next() podemos pegar o primeiro projeto que tem o nome correspondente
    project = next(
        (p for p in projects if p['project_name'] == project_name), None
    )
    assert project is not None, f"Project '{project_name}' does not exist."
    
    # Busca os teams do projeto
    all_teams_in_projects = project.get('teams', [])
    
    # Extrai os nomes dos teams (assumindo que são objetos com team_name)
    team_names = [team['team_name'] for team in all_teams_in_projects]
    
    updated_team_name = context['team_name']  # Já foi atualizado no step anterior
    
    assert updated_team_name in team_names, (
        f"Updated team '{updated_team_name}' not found in project '{project_name}'. Found: {team_names}"
    )