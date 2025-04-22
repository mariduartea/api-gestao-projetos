from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from fastapi_zero.app import app
from fastapi_zero.models import table_registry
from fastapi_zero.database import get_user_by_email


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    table_registry.metadata.create_all(engine)

    # gerenciamento de contexto
    with Session(engine) as session:
        yield session  # o yield delimita o setup, que roda antes do teste

    table_registry.metadata.drop_all(engine)  # teardown


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1), ):
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
def create_user(client,
                username="testusername",
                email="teste@teste.com",
                password="password"
                ):
    return client.post(
        '/users/',
        json={
            'username': username,
            'email': email,
            'password': password
        }
    )
