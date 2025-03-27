from sqlalchemy import select

from fastapi_zero.models import User


def test_create_user(session):
    user = User(
        username='mari',
        email='mari2@email.com',
        password='minhasenha',
    )

    session.add(user)
    session.commit()

    result = session.scalar(
        select(User).where(User.email == 'mari2@email.com')
    )

    assert result.username == 'mari'
