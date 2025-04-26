from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from fastapi_zero.models import User
from fastapi_zero.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def get_session():  # pragma: no cover
    with Session(engine) as session:
        yield session


def get_user_count(session: Session) -> int:
    """Get the count of users in the database."""
    return len(session.execute(select(User)).all())
