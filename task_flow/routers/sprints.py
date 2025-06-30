from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from task_flow.database import get_session
from task_flow.models import User, Sprint, Project
from task_flow.schemas import SprintPublic, SprintSchema
from task_flow.security import get_current_user

router = APIRouter(prefix='/sprints', tags=['sprints'])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=SprintPublic, status_code=HTTPStatus.CREATED)
def create_sprint(
    sprints: SprintSchema, session: T_Session, current_user: T_CurrentUser
):
    # Buscar o projeto pelo nome
    project = session.query(Project).filter_by(project_name=sprints.project_name).first()
    if not project:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Projet not found")

    db_sprint = Sprint(
        sprint_name=sprints.sprint_name,
        project_id=project.id,
        start_date=sprints.start_date,
        end_date=sprints.end_date,
        description=sprints.description,
        current_user_id=current_user.id
    )

    session.add(db_sprint)
    session.commit()
    session.refresh(db_sprint)
    return SprintPublic(
        id=db_sprint.id,
        sprint_name=db_sprint.sprint_name,
        project_name=project.project_name,
        start_date=db_sprint.start_date,
        end_date=db_sprint.end_date,
        description=db_sprint.description,
    )