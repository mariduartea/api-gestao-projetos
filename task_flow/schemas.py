from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from task_flow.settings import Settings

settings = Settings()


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str | None
    email: EmailStr
    password: str

    @field_validator('password')
    def password_must_be_long_enough(cls, value):
        if len(value) < settings.MIN_PASSWORD_LENGTH:
            raise ValueError('Password must have at least 6 characters')
        return value


class UserDB(UserSchema):
    id: int


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str  # o teoken JWT que vamos gerar
    token_type: str  # o modelo que o cliente deve usar para Autorização


class TeamSchema(BaseModel):
    team_name: str
    user_list: List[str]


class TeamPublic(BaseModel):
    id: int
    team_name: str
    users: List[UserPublic]


class TeamUpdateSchema(BaseModel):
    team_name: str | None = None
    user_list: list[str] | None = None


class FilterTeam(BaseModel):
    team_name: str | None = None


class ProjectSchema(BaseModel):
    project_name: str
    team_list: List[str]


class ProjectPublic(BaseModel):
    id: int
    project_name: str
    teams: List[TeamPublic]


class FilterProject(BaseModel):
    project_name: str | None = None


class ProjectUpdateSchema(BaseModel):
    project_name: str | None = None
    team_list: list[str] | None = None
