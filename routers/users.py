from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Email
from schemas import UserCreate, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(Email).filter(Email.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        first_name = data.first_name,
        last_name  = data.last_name,
        password        = data.password,
        gender          = data.gender,
        date_of_birth   = data.date_of_birth,
        height          = data.height,
        weight          = data.weight,
        fitness_level   = data.fitness_level,
        fitness_goals   = data.fitness_goals,
    )
    db.add(user)
    db.flush()

    email_row = Email(user_id=user.user_id, email=data.email)
    db.add(email_row)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user