from http import HTTPStatus

import pytest
from pytest_bdd import given, scenarios, then, when
from utils.helpers import (
    authentication,
    create_random_project_via_api,
    create_random_team_via_api,
    create_random_user_direct,
    update_project,
)

scenarios('../features/projects.feature')


@pytest.fixture
def context():
    return {}


# CT001
@given('a random user is created')
def random_user_is_created(session, context):
    create_random_user_direct(session, context)


@given('a random team is created with that user')
def random_team_is_created(client, context):
    authentication(client, context)
    create_random_team_via_api(client, context)


@given('a random project is created with that team')
def create_a_project(client, context):
    project = create_random_project_via_api(client, context)
    context['project'] = project


@when('the user updates the project name')
def update_project_name(client, context):
    new_name = f'Super {context["project"]["project_name"]}'

    project_id = context['project']['id']
    response = update_project(
        client=client,
        project_id=project_id,
        project_data={'project_name': new_name},
        headers=context['headers'],
    )

    context['updated_project_name'] = new_name
    assert response.status_code == HTTPStatus.OK


@then('the project list should display the updated name')
def verify_project_name_updated(client, context):
    response = client.get('/projects/', headers=context['headers'])

    projects = response.json()
    project = next(
        (
            project
            for project in projects
            if project['project_name'] == context['updated_project_name']
        ),
        None,
    )
    assert project is not None, 'Updated project not found in project list'


# CT002
@given('the user updates the project teams')
def update_project_team(client, context):
    project_id = context['project']['id']

    team1 = create_random_team_via_api(client, context)
    team2 = create_random_team_via_api(client, context)
    new_team_list = [team1['team_name'], team2['team_name']]

    response = update_project(
        client=client,
        project_id=project_id,
        headers=context['headers'],
        project_data={'team_list': new_team_list},
    )

    context['updated_team_list'] = new_team_list
    assert response.status_code == HTTPStatus.OK


@when('the user deletes the project')
def user_delete_the_project(client, context):
    project_id = context['project']['id']

    response = client.delete(
        f'/projects/{project_id}', headers=context['headers']
    )

    assert response.status_code == HTTPStatus.OK


@then('the project should no longer appear in the project list')
def verify_project_removed_from_system(client, context):
    project_id = context['project']['id']

    response = client.get(
        f'/projects/{project_id}', headers=context['headers']
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
