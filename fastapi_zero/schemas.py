from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from fastapi_zero.models import TodoState
from fastapi_zero.settings import Settings

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


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState  # classe especial do python que representa um enum


class TodoPublic(TodoSchema):
    id: int


class TodoList(BaseModel):
    todos: list[TodoPublic]


class FilterTodo(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
    offset: int | None = None
    limit: int | None = None


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
