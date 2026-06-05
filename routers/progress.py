from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import ProgressLog
from schemas import ProgressLogCreate

router = APIRouter()

@router.post("/{user_id}/log")
def log_progress(user_id: int, data: ProgressLogCreate, db: Session = Depends(get_db)):
    log = ProgressLog(user_id=user_id, **data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "Progress logged", "log_id": log.log_id}

@router.get("/{user_id}/history")
def get_progress_history(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(ProgressLog).filter(ProgressLog.user_id == user_id)\
             .order_by(ProgressLog.log_date.desc()).all()
    return logs