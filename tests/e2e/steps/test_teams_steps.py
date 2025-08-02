from http import HTTPStatus

import pytest
from pytest_bdd import given, scenarios, then, when
from utils.helpers import (
    add_team_to_project,
    authentication,
    cannot_create_project_with_invalid_team,
    create_random_project_via_api,
    create_random_team_direct,
    create_random_team_via_api,
    create_random_user_direct,
    delete_updated_team,
    find_team,
    find_team_by_id,
    update_team,
)

pytestmark = pytest.mark.e2e

scenarios('../features/teams.feature')


@pytest.fixture
def context():
    return {}


# Steps em comum de todos os cenários
@given('the API has a registered team')
def verify_registered_team(session, client, context):
    context.clear()
    create_random_user_direct(session, context)
    authentication(client, context)
    create_random_team_via_api(client, context)


@given('this team is associated with a project')
def verify_associated_team_with_project(client, context):
    create_random_project_via_api(client, context)


# Scenario: Update team and verify that the changes appear in the project list
@when('this team is edited')
def edit_team(client, context):
    new_team_name = f'Updated {context["team_name"]}'
    response = update_team(
        client=client,
        team_id=context['team_id'],
        team_data={'team_name': new_team_name},
        headers=context['headers'],
    )
    assert response.status_code == HTTPStatus.OK, (
        f'Error while updating team: {response.json()}'
    )
    # Atualiza o context com o novo nome
    context['team_name'] = new_team_name


@then('the updates should be reflected in the project')
def verify_updated_team_in_project(client, context):
    response = client.get('/projects/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK, (
        f'Error while fetching projects: {response.json()}'
    )
    projects = response.json()
    project_name = context['project_name']
    # Com o next() podemos pegar o primeiro projeto com nome correspondente
    project = next(
        (p for p in projects if p['project_name'] == project_name), None
    )
    assert project is not None, f"Project '{project_name}' does not exist."

    all_teams_in_projects = project.get('teams', [])
    team_names = [team['team_name'] for team in all_teams_in_projects]

    updated_team_name = context['team_name']

    assert updated_team_name in team_names, (
        f"Updated team '{updated_team_name}' not found in project "
        f"'{project_name}'. Found: {team_names}"
    )


# Scenario: Deleting a team and verify if it doesn't exist in a certain project
@given('another random team is created')
def create_another_team(session, context):
    another_team = create_random_team_direct(session, context)
    context['another_team'] = another_team


@given('the project list is updated with the new team')
def create_project(client, context):
    authentication(client, context)
    response = client.get('/projects/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK

    projects = response.json()
    project = next(
        (p for p in projects if p['project_name'] == context['project_name']),
        None,
    )
    assert project is not None
    project_id = project['id']
    context['project_id'] = project_id

    # adicionar novo time à lista de projetos
    team_list = [team['team_name'] for team in project['teams']]
    team_list.append(context['another_team']['team_name'])

    response = add_team_to_project(
        client,
        context['project_id'],
        context['project_name'],
        team_list,
        context['headers'],
    )

    # FAZ NOVO GET para ver o efeito real
    response = client.get('/projects/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK


@when('the team is deleted')
def delete_team(client, context):
    response = client.delete(
        f'/teams/{context["team_id"]}', headers=context['headers']
    )

    assert response.status_code == HTTPStatus.OK, (
        f'Error while deleting team: {response.json()}'
    )


@then('the deleted team have to disappear in project list')
def verify_no_deleted_team_in_project(client, context):
    response = client.get('/projects/', headers=context['headers'])
    assert response.status_code == HTTPStatus.OK, (
        f'Error while fetching projects: {response.json()}'
    )
    projects = response.json()
    project_name = context['project_name']

    # Com o next() podemos pegar o primeiro projeto com nome correspondente
    project = next(
        (p for p in projects if p['project_name'] == project_name), None
    )
    assert project is not None, f"Project '{project_name}' does not exist."
    teams_names = [t['team_name'] for t in project['teams']]
    assert context['another_team']['team_name'] not in teams_names, (
        f"Team '{context['another_team']['team_name']}' was not deleted "
        f'from project: {teams_names}'
    )


# Scenario: Successful end-to-end flow with a team
@given('a user is created')
def create_user(client, session, context):
    create_random_user_direct(session, context)
    authentication(client, context)


@when('the user creates a new team')
def create_team(client, context):
    create_random_team_via_api(client, context)


@then('the team appears in the team list')
def get_teams_list(client, context):
    response = find_team(client, context['headers'], context['team_name'])
    assert response is not None, (
        f"Team '{context['team_name']}' not found in the team list"
    )


@then('the team can be retrieved by its ID')
def get_team_by_id(client, context):
    response = find_team_by_id(client, context['headers'], context['team_id'])
    assert response is not None, (
        f'Team with ID {context["team_id"]} was not found.'
    )


# @when("the user updates the team data")
# def edit_team(client, context):
#     new_team_name = f'Updated {context["team_name"]}'
#     response = update_team(client, context['team_id'],
#                        team_data={
#                            'team_name': new_team_name
#                            },
#                         headers=context['headers'])
#     assert response.status_code == HTTPStatus.OK, (
#         f'Error while updating team: {response.json()}'
#     )
#     # Atualiza o context com o novo nome
#     context['team_name'] = new_team_name


@then('the updated team appears in the team list')
def get_updated_team_in_teams_list(client, context):
    response = find_team(client, context['headers'], context['team_name'])
    assert response is not None, (
        f"Team '{context['team_name']}' not found in the team list"
    )


@then('the updated team can be retrieved by its ID')
def get_updated_team_by_id(client, context):
    response = find_team_by_id(client, context['headers'], context['team_id'])
    assert response is not None, (
        f'Team with ID {context["team_id"]} was not found.'
    )


@when('the user deletes the team')
def delete_recently_updated_team(client, context):
    response = delete_updated_team(
        client, context['headers'], context['team_id']
    )
    assert response.get('message') == 'Team deleted successfully', (
        f'Team with ID {context["team_id"]} was not deleted successfully'
    )


@then('the team no longer appears in the team list')
def deleted_team_not_in_teams_list(client, context):
    response = find_team(client, context['headers'], context['team_name'])
    assert response is None, (
        f"Team '{context['team_name']}' was found in the team list"
    )


@then('the team cannot be retrieved by its ID')
def deleted_team_not_found_by_id(client, context):
    response = find_team_by_id(client, context['headers'], context['team_id'])
    assert response is None, f'Team with ID {context["team_id"]} was found.'


# Scenario: Creating a project with a deleted team returns an error
@given('a team is created')
def create_user_and_team(client, context, session):
    create_random_user_direct(session, context)
    authentication(client, context)
    create_random_team_via_api(client, context)


# @when("the team is deleted")
# def delete_team(client, context):
#     response = client.delete(
#         f'/teams/{context["team_id"]}',
#         headers=context['headers']
#     )

#     assert response.status_code == HTTPStatus.OK, (
#         f'Error while deleting team: {response.json()}'
#     )


@then(
    'creating a project with the deleted team should fail with '
    "'One or more teams do not exist' error"
)
def verify_not_found_team_message(client, context):
    cannot_create_project_with_invalid_team(client, context)
