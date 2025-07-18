from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from task_flow.database import get_session
from task_flow.models import Project, Team, User
from task_flow.schemas import (
    FilterProject,
    Message,
    ProjectPublic,
    ProjectSchema,
    ProjectUpdateSchema,
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
def create_project(
    projects: ProjectSchema, session: T_Session, current_user: T_CurrentUser
):
    teams = (
        session.query(Team)
        .filter(Team.team_name.in_(projects.team_list))
        .all()
    )
    if len(teams) != len(projects.team_list):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='One or more teams do not exist',
        )

    if len(projects.team_list) == 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Project must have at least one team',
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

    db_projects = Project(
        project_name=projects.project_name, current_user_id=current_user.id
    )
    db_projects.teams = teams

    session.add(db_projects)
    session.commit()
    session.refresh(db_projects)
    return db_projects


@router.get('/', response_model=List[ProjectPublic])
def read_projects(
    session: T_Session,
    project_filter: Annotated[FilterProject, Query()],
    current_user: T_CurrentUser,
):
    query = select(Project)

    if project_filter.project_name:
        query = query.filter(
            Project.project_name.contains(project_filter.project_name)
        )

    db_projects = session.scalars(query).all()

    if not db_projects:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Project not found',
        )

    return db_projects


@router.get('/{projects_id}', response_model=ProjectPublic)
def read_projects_with_id(
    session: T_Session,
    projects_id: int,
    current_user: T_CurrentUser,
):
    query = select(Project).where(Project.id == projects_id)
    project = session.scalar(query)
    # projects é uma lista
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Project not found'
        )

    return project


@router.patch('/{projects_id}', response_model=ProjectPublic)
def update_project(
    session: T_Session,
    current_user: T_CurrentUser,
    projects_id: int,
    project_update: ProjectUpdateSchema,
):
    project = session.scalar(select(Project).where(Project.id == projects_id))
    # Inserir project_id inválido
    if not project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Project not found'
        )
    # Inserir um projeto não criado pelo usuário logado
    if project.current_user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You are not allowed to update this project. '
            'Only the team owner can perform this action.',
        )

    if project_update.project_name is not None:
        existing_project = session.scalar(
            select(Project).where(
                Project.project_name == project_update.project_name,
                Project.id != projects_id,
            )
        )
        # não permitir que altere o nome do projeto para um outro que já exista
        if existing_project:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Project name already exists',
            )
        # alterar o nome do projeto com sucesso
        project.project_name = project_update.project_name

    # Atualiza os times do projeto
    if project_update.team_list is not None:
        # busca no banco os times escolhidos
        teams = (
            session.query(Team)
            .filter(Team.team_name.in_(project_update.team_list))
            .all()
        )
        if len(teams) != len(project_update.team_list):
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Teams not found'
            )
        if not teams:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail='Project must have at least one team',
            )
        project.teams = teams
    session.commit()
    session.refresh(project)
    return project


@router.delete('/{project_id}', response_model=Message)
def delete_project(
    session: T_Session, current_user: T_CurrentUser, project_id: int
):
    project = session.scalar(select(Project).where(Project.id == project_id))

    if not project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Project not found'
        )

    if project.current_user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You are not allowed to delete this project. '
            'Only the project owner can perform this action.',
        )

    session.delete(project)
    session.commit()

    return {'message': 'Project deleted successfully'}
