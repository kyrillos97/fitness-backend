from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import WorkoutPlan, WorkoutDay, Exercise, PlanArchive
from schemas import WorkoutPlanCreate, WorkoutPlanResponse

router = APIRouter()

@router.post("/{user_id}/plan", response_model=WorkoutPlanResponse)
def create_or_update_workout_plan(user_id: int, data: WorkoutPlanCreate, db: Session = Depends(get_db)):
    # Archive old plan if exists
    old = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id,
        WorkoutPlan.is_active == True
    ).first()

    next_version = 1
    if old:
        db.add(PlanArchive(
            user_id   = user_id,
            plan_type = "workout",
            reason    = "user_updated",
            plan_data = {
                "plan_name":        old.plan_name,
                "version":          old.version,
                "weekly_frequency": old.weekly_frequency,
                "difficulty_level": old.difficulty_level,
            }
        ))
        old.is_active = False
        next_version = old.version + 1

    new_plan = WorkoutPlan(
        user_id          = user_id,
        plan_name        = data.plan_name,
        weekly_frequency = data.weekly_frequency,
        difficulty_level = data.difficulty_level,
        version          = next_version,
        is_active        = True,
        created_by       = "user",
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

@router.get("/{user_id}/plan", response_model=WorkoutPlanResponse)
def get_active_workout_plan(user_id: int, db: Session = Depends(get_db)):
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id  == user_id,
        WorkoutPlan.is_active == True
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="No active workout plan found")
    return plan