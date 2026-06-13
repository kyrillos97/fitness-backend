from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import date, datetime

class UserCreate(BaseModel):
    first_name: str
    last_name:  str
    email:           EmailStr
    password:        str
    gender:          Optional[str] = None
    date_of_birth:   Optional[date] = None
    height:          Optional[float] = None
    weight:          Optional[float] = None
    fitness_level:   Optional[str] = None
    fitness_goals:   Optional[List[str]] = None

class UserResponse(BaseModel):
    user_id:         int
    first_name: str
    last_name:  str
    is_active:       bool

    class Config:
        from_attributes = True


class UserByEmailResponse(BaseModel):
    user_id:       int
    first_name:    str
    last_name:     str
    is_active:     bool
    fitness_level: Optional[str]       = None
    fitness_goals: Optional[List[str]] = None
    height:        Optional[float]     = None
    weight:        Optional[float]     = None

    class Config:
        from_attributes = True

class DietPlanCreate(BaseModel):
    plan_name:             str
    daily_calories_target: float
    protein_target:        float
    carbs_target:          float
    fat_target:            float

class DietPlanResponse(BaseModel):
    diet_plan_id:          int
    plan_name:             str
    version:               int
    is_active:             bool
    daily_calories_target: float

    class Config:
        from_attributes = True

class ProgressLogCreate(BaseModel):
    weight:                Optional[float] = None
    bmi:                   Optional[float] = None
    body_fat:              Optional[float] = None
    skeletal_muscle:       Optional[float] = None
    rpe:                   Optional[float] = None
    energy_level:          Optional[int]   = None
    log_date:              Optional[date]  = None
    notes:                 Optional[str]   = None
    completed_exercises:   Optional[List[Any]] = None
    incompleted_exercises: Optional[List[Any]] = None