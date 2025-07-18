from contextlib import contextmanager
from datetime import datetime

import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from task_flow.app import app
from task_flow.database import get_session
from task_flow.models import (
    Project,
    Team,
    User,
    table_registry,
)
from task_flow.schemas import TeamSchema
from task_flow.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}+senha')


class TeamFactory(factory.Factory):
    class Meta:
        model = Team

    team_name = factory.Faker('company')


class ProjectFactory(factory.Factory):
    class Meta:
        model = Project

    project_name = factory.Faker('color_name')


@pytest.fixture
def client(session):  # o session é uma fixture que retorna um gerador
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client  # o yield delimita o setup, que roda antes do teste

    app.dependency_overrides.clear()  # teardown


# fix que faz a conexão com o bd, executada 1x por sessão de teste
@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_engine(postgres.get_connection_url())

        with _engine.begin():
            yield _engine  # o yield delimita o setup, que roda antes do teste


# fixture executada em cada teste, que cria a tabela e faz o drop
@pytest.fixture
def session(engine):
    table_registry.metadata.create_all(engine)

    # gerenciamento de contexto
    with Session(engine) as session:
        yield session  # o yield delimita o setup, que roda antes do teste

    table_registry.metadata.drop_all(engine)  # teardown


@contextmanager
def _mock_db_time(
    *,
    model,
    time=datetime(2024, 1, 1),
):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def user(session):
    pwd = 'testtest'

    user = UserFactory(password=get_password_hash(pwd))

    session.add(user)
    session.commit()
    session.refresh(user)

    # Monkey Patch adicionando o password limpo no objeto user
    user.clean_password = pwd

    return user


@pytest.fixture
def other_user(session):
    user = UserFactory()
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    return response.json()['access_token']


# fixture criada para garantir que o token
# de team_with_users esteja sendo passado corretamente
@pytest.fixture
def owner_token(client, users):
    # users[0] é o dono do time em team_with_users
    user = users[0]
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    return response.json()['access_token']


@pytest.fixture
def another_owner_token(client, users):
    # users[1] é o dono do time em another_team_with_same_name
    user = users[1]
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


@pytest.fixture
def users(session):
    pwd = 'testtest'
    users = [UserFactory(password=get_password_hash(pwd)) for _ in range(3)]
    session.add_all(users)
    session.commit()
    for user in users:
        session.refresh(user)
        user.clean_password = pwd
    return users


@pytest.fixture
def team_with_users(session, users):
    team = TeamFactory(current_user_id=users[0].id)
    team.users = users  # Relacionamento muitos-para-muitos
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@pytest.fixture
def team_list(session, users):
    teams = []
    for i in range(3):
        team = TeamFactory(
            team_name=f'team{i}', current_user_id=users[i % len(users)].id
        )
        team.users = [users[i % len(users)]]
        session.add(team)
        teams.append(team)
    session.commit()
    for team in teams:
        session.refresh(team)
    return teams  # retorna os objetos do model Team diretamente


@pytest.fixture
def other_team_list(session, users):
    teams = []
    for i in range(3):
        team = TeamFactory(
            team_name=f'other_team{i}',
            current_user_id=users[(i + 1) % len(users)].id,
        )
        team.users = [users[(i + 1) % len(users)]]
        session.add(team)
        teams.append(team)
    session.commit()
    for team in teams:
        session.refresh(team)
    return teams


@pytest.fixture
def team_dict_list(team_list):
    return [TeamSchema.from_orm(team).dict() for team in team_list]


@pytest.fixture
def another_team_with_same_name(session, users):
    team = TeamFactory(team_name='nome_duplicado', current_user_id=users[1].id)
    team.users = users
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@pytest.fixture
def projects_with_teams(session, team_list, users):
    project = ProjectFactory(current_user_id=users[0].id)
    project.teams = team_list  # Relacionamento muitos-para-muitos
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@pytest.fixture
def another_project_with_same_name(session, team_list, users):
    project = ProjectFactory(
        project_name='nome_duplicado', current_user_id=users[0].id
    )
    project.teams = team_list
    session.add(project)
    session.commit()
    session.refresh(project)
    return project
