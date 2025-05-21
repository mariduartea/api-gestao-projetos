from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from task_flow.database import get_session
from task_flow.models import Team, User
from task_flow.schemas import TeamPublic, TeamSchema

router = APIRouter(prefix='/teams', tags=['teams'])

Session = Annotated[Session, Depends(get_session)]  # montando o objeto session


@router.post('/', response_model=TeamPublic, status_code=HTTPStatus.CREATED)
def create_teams(teams: TeamSchema, session: Session):
    users = (
        session.query(User).filter(User.username.in_(teams.user_list)).all()
    )
    if len(users) != len(teams.user_list):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='One or more users do not exist',
        )

    db_teams = session.scalar(
        select(Team).where((Team.team_name == teams.team_name))
    )

    if db_teams:
        if db_teams.team_name == teams.team_name:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Team already created',
            )

    db_teams = Team(
        team_name=teams.team_name,
    )
    db_teams.users = users

    session.add(db_teams)
    session.commit()
    session.refresh(db_teams)
    return db_teams
