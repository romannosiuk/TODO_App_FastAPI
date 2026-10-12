import os
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Path, status
from starlette import status
from starlette.requests import Request

from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user, SECRET_KEY, ALGORITHM
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError

templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=templates_dir)


router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[SessionLocal, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access-token")
    return redirect_response

### Pages ###
@router.get("/todo-page", status_code=status.HTTP_200_OK)
async def render_todo_page(request: Request, db: db_dependency):
    token = request.cookies.get("access_token")
    if not token:
        return redirect_to_login()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('user_role')
        if username is None or user_id is None:
            return redirect_to_login()

        user = {'username': username, 'id': user_id, 'user_role': user_role}
        todos = db.query(Todos).filter(Todos.owner_id == user_id).all()
        return templates.TemplateResponse(
            request=request,
            name="todo.html",
            context={"todos": todos, "user": user}
        )
    except JWTError:
        return redirect_to_login()

@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return redirect_to_login()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('user_role')
        if username is None or user_id is None:
            return redirect_to_login()

        user = {'username': username, 'id': user_id, 'user_role': user_role}
        return templates.TemplateResponse(
            request=request,
            name="add-todo.html",
            context={"user": user}
        )
    except JWTError:
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    token = request.cookies.get("access_token")
    if not token:
        return redirect_to_login()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('user_role')
        if username is None or user_id is None:
            return redirect_to_login()

        user = {'username': username, 'id': user_id, 'user_role': user_role}
        todo = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user_id).first()
        if not todo:
            return redirect_to_login()

        return templates.TemplateResponse(
            request=request,
            name="edit-todo.html",
            context={"todo": todo, "user": user}
        )
    except JWTError:
        return redirect_to_login()


### Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = Todos(**todo_request.model_dump(), owner_id = user.get('id'))

    db.add(todo_model)
    db.commit()

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not Found")
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
    db.commit()


