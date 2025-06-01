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
from task_flow.models import Team, Todo, TodoState, User, table_registry
from task_flow.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}+senha')


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


class TeamFactory(factory.Factory):
    class Meta:
        model = Team

    team_name = factory.Faker('text')


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


@pytest.fixture
def users(session):
    users = [UserFactory() for _ in range(3)]
    session.add_all(users)
    session.commit()
    for user in users:
        session.refresh(user)
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
def another_team_with_same_name(session, users):
    team = TeamFactory(team_name='nome_duplicado', current_user_id=users[1].id)
    team.users = users
    session.add(team)
    session.commit()
    session.refresh(team)
    return team
