# biblioteca padrão
from http import HTTPStatus

from fastapi import FastAPI

from task_flow.routers import auth, projects, teams, users
from task_flow.schemas import Message

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(teams.router)

app.include_router(projects.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World'}
