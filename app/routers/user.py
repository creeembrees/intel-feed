from fastapi import FastAPI, Response, status, Request, Depends, HTTPException, APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..schemas import User, UserCreate, UserBase
from ..databases import get_db

router = APIRouter()

@router.post("/user", status_code=status.HTTP_201_CREATED, response_model=schemas.UserBase)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    try:
        hashed_password = utils.hash(user.password[:72])
    except Exception as e:
        raise HTTPException(status_code=400, detail="Password can't be hashed. Ensure it meets the requirements.")
    
    db_user = models.User(email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/user/{id}", response_model=schemas.UserBase)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
