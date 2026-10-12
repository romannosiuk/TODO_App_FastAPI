from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Todos, Users
from ..database import SessionLocal
from .auth import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[SessionLocal, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_info(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found.')
    return user_model