from pydantic import BaseModel, EmailStr, field_validator

from fastapi_zero.settings import Settings

settings = Settings()


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str | None
    email: EmailStr
    password: str

    @field_validator("password")
    def password_must_be_long_enough(cls, value):
        if len(value) < settings.MIN_PASSWORD_LENGTH:
            raise ValueError("Password must have at least 6 characters")
        return value


class UserDB(UserSchema):
    id: int


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserList(BaseModel):
    users: list[UserPublic]
