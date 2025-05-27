from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from task_flow.database import get_session
from task_flow.models import Team, User
from task_flow.schemas import FilterTeam, TeamPublic, TeamSchema
from task_flow.security import get_current_user

router = APIRouter(
    prefix='/teams',
    tags=['teams'],
    #    dependencies=[Depends(get_current_user)]
)

T_Session = Annotated[Session, Depends(get_session)]
# montando o objeto session
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TeamPublic, status_code=HTTPStatus.CREATED)
def create_teams(
    teams: TeamSchema, session: T_Session, current_user: T_CurrentUser
):
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

    db_teams = Team(team_name=teams.team_name, current_user_id=current_user.id)
    db_teams.users = users

    session.add(db_teams)
    session.commit()
    session.refresh(db_teams)
    return db_teams


@router.get('/', response_model=List[TeamPublic])
def read_teams(
    session: T_Session,
    team_filter: Annotated[FilterTeam, Query()],
    current_user: T_CurrentUser,
):
    query = select(Team)

    if team_filter.team_name:
        query = query.filter(Team.team_name.contains(team_filter.team_name))

    teams = session.scalars(query).all()

    return teams
