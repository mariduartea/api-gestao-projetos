from datetime import datetime

from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


teams_users = Table(
    'teams_users',
    table_registry.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('team_id', ForeignKey('teams.id'), primary_key=True),
)

projects_teams = Table(
    'projects_teams',
    table_registry.metadata,
    Column('project_id', ForeignKey('projects.id'), primary_key=True),
    Column('team_id', ForeignKey('teams.id'), primary_key=True),
)


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    teams: Mapped[list['Team']] = relationship(
        'Team', secondary=teams_users, back_populates='users', init=False
    )


@table_registry.mapped_as_dataclass
class Team:
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    team_name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    current_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    users: Mapped[list[User]] = relationship(
        'User', secondary=teams_users, back_populates='teams', init=False
    )
    projects: Mapped[list['Project']] = relationship(
        'Project', secondary=projects_teams, back_populates='teams', init=False
    )


@table_registry.mapped_as_dataclass
class Project:
    __tablename__ = 'projects'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    project_name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    current_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    teams: Mapped[list[Team]] = relationship(
        'Team', secondary=projects_teams, back_populates='projects', init=False
    )
