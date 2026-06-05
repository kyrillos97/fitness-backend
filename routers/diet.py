from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import DietPlan, PlanArchive
from schemas import DietPlanCreate, DietPlanResponse

router = APIRouter()

@router.post("/{user_id}/plan", response_model=DietPlanResponse)
def create_or_update_diet_plan(user_id: int, data: DietPlanCreate, db: Session = Depends(get_db)):
    old = db.query(DietPlan).filter(DietPlan.user_id == user_id, DietPlan.is_active == True).first()
    next_version = 1
    if old:
        db.add(PlanArchive(
            user_id=user_id, plan_type="diet", reason="user_updated",
            plan_data={"plan_name": old.plan_name, "version": old.version}
        ))
        old.is_active = False
        next_version = old.version + 1

    new_plan = DietPlan(
        user_id               = user_id,
        plan_name             = data.plan_name,
        daily_calories_target = data.daily_calories_target,
        protein_target        = data.protein_target,
        carbs_target          = data.carbs_target,
        fat_target            = data.fat_target,
        version               = next_version,
        is_active             = True,
        created_by            = "user",
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

@router.get("/{user_id}/plan", response_model=DietPlanResponse)
def get_active_diet_plan(user_id: int, db: Session = Depends(get_db)):
    plan = db.query(DietPlan).filter(DietPlan.user_id == user_id, DietPlan.is_active == True).first()
    if not plan:
        raise HTTPException(status_code=404, detail="No active diet plan")
    return plan