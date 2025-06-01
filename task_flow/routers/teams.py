from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from task_flow.database import get_session
from task_flow.models import Team, User
from task_flow.schemas import (
    FilterTeam,
    TeamPublic,
    TeamSchema,
    TeamUpdateSchema,
)
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

    db_teams = session.scalars(query).all()

    if not db_teams:  # Lista vazia é False
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Team does not exist',
        )

    return db_teams


@router.get('/{team_id}', response_model=TeamPublic)
def read_teams_with_id(
    session: T_Session, current_user: T_CurrentUser, team_id: int
):
    query = select(Team).where(Team.id == team_id)
    teams = session.scalar(query)

    if teams is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Team does not exist',
        )

    return teams


@router.patch('/{team_id}', response_model=TeamPublic)
def update_team(
    session: T_Session,
    current_user: T_CurrentUser,
    team_id: int,
    team_update: TeamUpdateSchema,
):
    query = select(Team).where(Team.id == team_id)
    team = session.scalar(query)
    if not team:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Team does not exist',
        )

    # Atualiza o nome do time
    if team_update.team_name is not None:
        existing_team = session.scalar(
            select(Team).where(
                Team.team_name == team_update.team_name, Team.id != team_id
            )
        )  # Não considerar o próprio time
        if existing_team:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Team name alreaty exists',
            )
        team.team_name = team_update.team_name

    # Atualiza os usuários do time
    if team_update.user_list is not None:
        users = (
            session.query(User)
            .filter(User.username.in_(team_update.user_list))
            .all()
        )
        if len(users) != len(team_update.user_list):
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Users not found',
            )
        if not users:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail='Team must have at least one user',
            )
        team.users = users

    session.commit()
    session.refresh(team)
    return team  # Sempre retorne o objeto atualizado
