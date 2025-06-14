from task_flow.models import Team


def assert_team_has_users(team, expected_users):
    returned_usernames = {u['username'] for u in team['users']}
    expected_usernames = {u.username for u in expected_users}
    assert returned_usernames == expected_usernames


def assert_project_has_teams(project, expected_teams):
    returned_team_names = {t['team_name'] for t in project['teams']}
    expected_teams = {t.team_name for t in expected_teams}
    assert returned_team_names == expected_teams


def get_team_by_id(response_json, team_id):
    """Busca um time pelo id no response.json()."""
    return next((t for t in response_json if t['id'] == team_id), None)


def get_project_by_id(response_json, project_id):
    return next((p for p in response_json if p['id'] == project_id), None)


def get_team_count(session):
    return session.query(Team).count()
