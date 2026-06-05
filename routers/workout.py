from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import WorkoutPlan, PlanArchive

router = APIRouter()

@router.get("/{user_id}/plan")
def get_active_workout_plan(user_id: int, db: Session = Depends(get_db)):
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id, WorkoutPlan.is_active == True).first()
    if not plan:
        raise HTTPException(status_code=404, detail="No active workout plan")
    return plan