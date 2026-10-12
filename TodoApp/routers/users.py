from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Users
from ..database import SessionLocal
from .auth import get_current_user, bcrypt_context
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[SessionLocal, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
# bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)



@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency,
                          db: db_dependency,
                          user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.old_password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password change")

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.put("/phone_number/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency,
                              db: db_dependency, phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()

