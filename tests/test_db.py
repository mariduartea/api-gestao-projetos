from dataclasses import asdict

from sqlalchemy import select

from fastapi_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='mari',
            email='mari2@email.com',
            password='minhasenha',
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.email == 'mari2@email.com'))

    assert asdict(user) == {
        'id': 1,
        'username': 'mari',
        'password': 'minhasenha',
        'email': 'mari2@email.com',
        'created_at': time,
        'updated_at': time,
    }
