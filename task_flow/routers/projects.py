from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from task_flow.database import get_session
from task_flow.models import Project, Team, User
from task_flow.schemas import (
    Message,
    ProjectPublic,
    ProjectSchema
)

from task_flow.security import get_current_user

router = APIRouter(
    prefix='/projects',
    tags=['projects'],
)

T_Session = Annotated[Session, Depends(get_session)]
# montando o objeto session
T_CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post('/', response_model=ProjectPublic, status_code=HTTPStatus.CREATED)
def create_teams(
        projects: ProjectSchema, session: T_Session, current_user: T_CurrentUser
):
    teams = (
        session.query(Team).filter(Team.team_name.in_(projects.team_list)).all()
    )
    if len(teams) != len(projects.team_list):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='One or more teams do not exist',
        )

    db_projects = session.scalar(
        select(Project).where((Project.project_name == projects.project_name))
    )

    if db_projects:
        # if db_teams.team_name == teams.team_name:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Project already created',
            )

    db_projects = Project(project_name=projects.project_name, current_user_id=current_user.id)
    db_projects.teams = teams

    session.add(db_projects)
    session.commit()
    session.refresh(db_projects)
    return db_projects