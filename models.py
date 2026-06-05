"""
models.py — SQLAlchemy ORM models
Every table and relationship from the project mapping document is defined here.

JSON columns are used for fields that:
  • Can contain multiple values (arrays / nested objects)
  • Change structure over time without schema migrations
  • Store complex nested data (plan snapshots, encoding vectors, etc.)
"""

import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, Float,
    DateTime, Date, Time, Text, LargeBinary,
    ForeignKey, Enum, Table,
)
from sqlalchemy.dialects.postgresql import JSON, JSONB   # JSONB for indexable JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


# ══════════════════════════════════════════════════════════════════════════════
# ENUM TYPES
# ══════════════════════════════════════════════════════════════════════════════

class FitnessLevelEnum(str, enum.Enum):
    beginner     = "Beginner"
    intermediate = "Intermediate"
    expert       = "Expert"


class GenderEnum(str, enum.Enum):
    male   = "Male"
    female = "Female"


class DifficultyLevelEnum(str, enum.Enum):
    beginner     = "Beginner"
    intermediate = "Intermediate"
    expert       = "Expert"


class ExecutionStatusEnum(str, enum.Enum):
    pending   = "pending"
    executing = "executing"
    completed = "completed"
    failed    = "failed"


class CompletionStatusEnum(str, enum.Enum):
    pending     = "pending"
    in_progress = "in_progress"
    completed   = "completed"


class PlanTypeEnum(str, enum.Enum):
    workout = "workout"
    diet    = "diet"


class MessageTypeEnum(str, enum.Enum):
    user   = "user"
    ai     = "ai"
    system = "system"


class AIAgentTypeEnum(str, enum.Enum):
    coach      = "coach"
    nutritionist = "nutritionist"
    motivator  = "motivator"
    general    = "general"


# ══════════════════════════════════════════════════════════════════════════════
# ASSOCIATION / JUNCTION TABLES  (many-to-many)
# ══════════════════════════════════════════════════════════════════════════════

# making_population: User ↔ PopulationInsight  (many-to-many)
making_population = Table(
    "making_population",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "insight_id",
        Integer,
        ForeignKey("population_insights.insight_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# ══════════════════════════════════════════════════════════════════════════════
# USER  (core entity — almost every table references this)
# ══════════════════════════════════════════════════════════════════════════════

class User(Base):
    __tablename__ = "users"

    user_id           = Column(Integer, primary_key=True, autoincrement=True, index=True)
    password          = Column(String(255), nullable=False)

    # JSON — a user can have multiple / evolving fitness goals
    fitness_goals     = Column(JSONB, nullable=True)
    # e.g. ["lose_weight", "build_muscle"] or [{"goal": "lose_weight", "target_kg": 5}]

    last_login        = Column(DateTime(timezone=True), nullable=True)
    registration_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active         = Column(Boolean, default=True, nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name  = Column(String(100), nullable=False)
    gender            = Column(Enum(GenderEnum), nullable=True)

    # Single fitness_level column (Beginner / Intermediate / Expert)
    fitness_level     = Column(Enum(FitnessLevelEnum), nullable=True)

    height            = Column(Float, nullable=True)   # centimetres
    weight            = Column(Float, nullable=True)   # kilograms
    subscription_type = Column(String(50), nullable=True)
    date_of_birth     = Column(Date, nullable=True)

    # ── Relationships ──────────────────────────────────────────────────────
    email             = relationship("Email",                back_populates="user",  uselist=False)
    profile           = relationship("UserProfile",          back_populates="user",  uselist=False)
    preferences       = relationship("UserPreferences",      back_populates="user",  uselist=False)
    face_image        = relationship("FaceImage",            back_populates="user",  uselist=False)

    progress_logs        = relationship("ProgressLog",          back_populates="user")
    rapa_decisions       = relationship("RAPADecision",         back_populates="user")
    chat_conversations   = relationship("ChatConversation",     back_populates="user")
    coaching_sessions    = relationship("DailyCoachingSession", back_populates="user")
    motivation_messages  = relationship("MotivationMessage",    back_populates="user")
    diet_plans           = relationship("DietPlan",             back_populates="user")
    training_jobs        = relationship("TrainingJob",          back_populates="user")
    plan_archives        = relationship("PlanArchive",          back_populates="user")
    workout_plans        = relationship("WorkoutPlan",          back_populates="user")
    workout_sessions     = relationship("WorkoutSession",       back_populates="user")
    strategy_performances = relationship("StrategyPerformance", back_populates="user")

    population_insights = relationship(
        "PopulationInsight",
        secondary=making_population,
        back_populates="users",
    )


# ══════════════════════════════════════════════════════════════════════════════
# EMAIL  (separate table as shown in mapping)
# ══════════════════════════════════════════════════════════════════════════════

class Email(Base):
    __tablename__ = "emails"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    email   = Column(String(255), unique=True, nullable=False, index=True)

    user = relationship("User", back_populates="email")


# ══════════════════════════════════════════════════════════════════════════════
# USER PROFILE
# ══════════════════════════════════════════════════════════════════════════════

class UserProfile(Base):
    __tablename__ = "user_profiles"

    profile_id    = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)

    # JSON — mirrors the user's current goals snapshot (can evolve independently)
    fitness_goals = Column(JSONB, nullable=True)
    # e.g. [{"goal": "gain_muscle", "priority": 1, "target_date": "2025-12-01"}]

    age           = Column(Integer, nullable=True)
    weight        = Column(Float, nullable=True)
    height        = Column(Float, nullable=True)
    fitness_level = Column(Enum(FitnessLevelEnum), nullable=True)
    gender        = Column(Enum(GenderEnum), nullable=True)

    user = relationship("User", back_populates="profile")


# ══════════════════════════════════════════════════════════════════════════════
# USER PREFERENCES
# ══════════════════════════════════════════════════════════════════════════════

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    preferences_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)

    # JSON — all array/complex fields that change over time
    preferred_meal_time = Column(JSONB, nullable=True)
    # e.g. {"breakfast": "08:00", "lunch": "13:00", "dinner": "19:00"}

    work_out_days = Column(JSONB, nullable=True)
    # e.g. ["Monday", "Wednesday", "Friday"]

    equipments = Column(JSONB, nullable=True)
    # e.g. ["dumbbells", "resistance_bands", "pull_up_bar"]

    injuries = Column(JSONB, nullable=True)
    # e.g. [{"body_part": "knee", "severity": "mild", "notes": "avoid deep squats"}]

    dislike_allergies = Column(JSONB, nullable=True)
    # e.g. ["gluten", "nuts", "lactose"]

    medical_conditions = Column(JSONB, nullable=True)
    # e.g. [{"condition": "hypertension", "severity": "controlled", "medication": "none"}]

    user = relationship("User", back_populates="preferences")


# ══════════════════════════════════════════════════════════════════════════════
# FACE IMAGE
# ══════════════════════════════════════════════════════════════════════════════

class FaceImage(Base):
    __tablename__ = "face_images"

    face_image_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)

    # JSON — 128-dimensional face embedding vector (face_recognition library output)
    face_encoding = Column(JSONB, nullable=True)
    # e.g. [0.1234, -0.5678, 0.9012, ...]   (128 floats)

    image_data    = Column(LargeBinary, nullable=True)   # raw binary (JPEG/PNG bytes)

    user = relationship("User", back_populates="face_image")


# ══════════════════════════════════════════════════════════════════════════════
# PROGRESS LOGS
# ══════════════════════════════════════════════════════════════════════════════

class ProgressLog(Base):
    __tablename__ = "progress_logs"

    log_id      = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    rpe          = Column(Float,   nullable=True)   # Rate of Perceived Exertion 0-10
    energy_level = Column(Integer, nullable=True)   # 1-10 scale
    pain_status  = Column(String(100), nullable=True)
    completed    = Column(Boolean, default=False)

    # Body composition metrics
    weight          = Column(Float, nullable=True)
    skeletal_muscle = Column(Float, nullable=True)
    fat_mass        = Column(Float, nullable=True)
    body_water      = Column(Float, nullable=True)
    bmi             = Column(Float, nullable=True)
    body_fat        = Column(Float, nullable=True)
    metabolic_rate  = Column(Float, nullable=True)
    total_score     = Column(Float, nullable=True)

    # JSON — lists of exercise references that change each session
    completed_exercises   = Column(JSONB, nullable=True)
    # e.g. [{"exercise_id": 1, "name": "Push-up", "sets_done": 3, "reps_done": 12}]

    incompleted_exercises = Column(JSONB, nullable=True)
    # e.g. [{"exercise_id": 2, "name": "Pull-up", "reason": "too fatigued"}]

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes      = Column(Text, nullable=True)
    log_time   = Column(Time(timezone=True), nullable=True)
    log_date   = Column(Date, nullable=True)

    user = relationship("User", back_populates="progress_logs")


# ══════════════════════════════════════════════════════════════════════════════
# RAPA DECISIONS  (AI-generated adaptive decisions)
# ══════════════════════════════════════════════════════════════════════════════

class RAPADecision(Base):
    __tablename__ = "rapa_decisions"

    decision_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    # JSON — all AI reasoning / action fields (structure evolves with model updates)
    emergency_alerts = Column(JSONB, nullable=True)
    # e.g. [{"alert_type": "overtraining", "message": "...", "severity": "high"}]

    hypothesis = Column(JSONB, nullable=True)
    # e.g. {"text": "User is over-reaching", "confidence": 0.87, "factors": ["high_rpe", "poor_sleep"]}

    action_taken = Column(JSONB, nullable=True)
    # e.g. [{"type": "reduce_volume", "description": "Reduced sets by 20%", "timestamp": "..."}]

    modification_instructions = Column(JSONB, nullable=True)
    # e.g. {"workout": {"reduce_sets": true}, "diet": {"increase_protein": true}}

    notification_message  = Column(Text, nullable=True)
    created_at            = Column(DateTime(timezone=True), server_default=func.now())
    execution_status      = Column(Enum(ExecutionStatusEnum), default=ExecutionStatusEnum.pending)
    weight_trend          = Column(Float, nullable=True)
    weighted_rpe          = Column(Float, nullable=True)
    analysis_window_days  = Column(Integer, nullable=True)
    analysis_date         = Column(Date, nullable=True)

    user = relationship("User", back_populates="rapa_decisions")


# ══════════════════════════════════════════════════════════════════════════════
# WORKOUT PLAN
# ══════════════════════════════════════════════════════════════════════════════

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    workout_plan_id  = Column(Integer, primary_key=True, autoincrement=True)
    user_id          = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    is_active        = Column(Boolean, default=True)
    created_by       = Column(String(50), nullable=True)   # "AI" | "admin" | "trainer"
    version          = Column(Integer, default=1)
    weekly_frequency = Column(Integer, nullable=True)
    difficulty_level = Column(Enum(DifficultyLevelEnum), nullable=True)
    plan_name        = Column(String(200), nullable=False)

    user         = relationship("User",        back_populates="workout_plans")
    workout_days = relationship("WorkoutDay",   back_populates="workout_plan", cascade="all, delete-orphan")
    sessions     = relationship("WorkoutSession", back_populates="workout_plan")


# ══════════════════════════════════════════════════════════════════════════════
# WORKOUT DAYS  (containing_exer relationship is FK on Exercise)
# ══════════════════════════════════════════════════════════════════════════════

class WorkoutDay(Base):
    __tablename__ = "workout_days"

    workout_day_id  = Column(Integer, primary_key=True, autoincrement=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.workout_plan_id", ondelete="CASCADE"), nullable=False, index=True)
    is_rest_day     = Column(Boolean, default=False)
    notes           = Column(Text, nullable=True)
    day_of_week     = Column(Integer, nullable=True)   # 0 = Monday … 6 = Sunday
    day_name        = Column(String(20), nullable=True) # "Monday", "Tuesday", …

    workout_plan = relationship("WorkoutPlan", back_populates="workout_days")
    exercises    = relationship("Exercise",    back_populates="workout_day", cascade="all, delete-orphan")


# ══════════════════════════════════════════════════════════════════════════════
# EXERCISES
# ══════════════════════════════════════════════════════════════════════════════

class Exercise(Base):
    __tablename__ = "exercises"

    exercise_id    = Column(Integer, primary_key=True, autoincrement=True)
    workout_day_id = Column(Integer, ForeignKey("workout_days.workout_day_id", ondelete="CASCADE"), nullable=False, index=True)

    sets_count     = Column(Integer, nullable=True)
    reps           = Column(Integer, nullable=True)
    rest_minutes   = Column(Float,   nullable=True)
    exercise_order = Column(Integer, nullable=True)
    notes          = Column(Text,    nullable=True)

    exercise_name        = Column(String(200), nullable=False)
    exercise_description = Column(Text, nullable=True)
    exercise_type        = Column(String(100), nullable=True)   # "strength" | "cardio" | "flexibility"

    # JSON — an exercise can target multiple muscles / need multiple pieces of equipment
    muscle_group     = Column(JSONB, nullable=True)
    # e.g. ["chest", "triceps", "anterior_deltoid"]

    equipment_needed = Column(JSONB, nullable=True)
    # e.g. ["barbell", "flat_bench"]

    # Difficulty flags (kept as separate booleans matching the mapping)
    difficulty_beginner     = Column(Boolean, default=False)
    difficulty_intermediate = Column(Boolean, default=False)
    difficulty_expert       = Column(Boolean, default=False)

    workout_day = relationship("WorkoutDay", back_populates="exercises")


# ══════════════════════════════════════════════════════════════════════════════
# WORKOUT SESSION
# ══════════════════════════════════════════════════════════════════════════════

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    session_id      = Column(Integer, primary_key=True, autoincrement=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.workout_plan_id", ondelete="SET NULL"), nullable=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)

    session_rating    = Column(Integer, nullable=True)   # 1-5 stars
    completion_status = Column(Enum(CompletionStatusEnum), default=CompletionStatusEnum.pending)
    session_date      = Column(Date, nullable=True)
    start_time        = Column(Time(timezone=True), nullable=True)
    end_time          = Column(Time(timezone=True), nullable=True)
    notes             = Column(Text, nullable=True)

    workout_plan = relationship("WorkoutPlan", back_populates="sessions")
    user         = relationship("User",        back_populates="workout_sessions")


# ══════════════════════════════════════════════════════════════════════════════
# CHAT CONVERSATION
# ══════════════════════════════════════════════════════════════════════════════

class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    conversation_id   = Column(Integer, primary_key=True, autoincrement=True)
    user_id           = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    start_date        = Column(DateTime(timezone=True), server_default=func.now())
    last_message_date = Column(DateTime(timezone=True), nullable=True)

    user     = relationship("User",        back_populates="chat_conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    summaries = relationship("ChatSummary", back_populates="conversation", cascade="all, delete-orphan")


# ══════════════════════════════════════════════════════════════════════════════
# CHAT HISTORY (individual messages)
# ══════════════════════════════════════════════════════════════════════════════

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    message_id      = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.conversation_id", ondelete="CASCADE"), nullable=False, index=True)
    ai_agent_type   = Column(Enum(AIAgentTypeEnum), nullable=True)
    timestamp       = Column(DateTime(timezone=True), server_default=func.now())
    message_content = Column(Text, nullable=False)
    message_type    = Column(Enum(MessageTypeEnum), nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("ChatConversation", back_populates="messages")


# ══════════════════════════════════════════════════════════════════════════════
# CHAT SUMMARIES
# ══════════════════════════════════════════════════════════════════════════════

class ChatSummary(Base):
    __tablename__ = "chat_summaries"

    summary_id      = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.conversation_id", ondelete="CASCADE"), nullable=False, index=True)
    start_index     = Column(Integer, nullable=True)   # first message index summarised
    end_index       = Column(Integer, nullable=True)   # last  message index summarised
    message_count   = Column(Integer, nullable=True)
    summary_text    = Column(Text, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("ChatConversation", back_populates="summaries")


# ══════════════════════════════════════════════════════════════════════════════
# DAILY COACHING SESSION
# ══════════════════════════════════════════════════════════════════════════════

class DailyCoachingSession(Base):
    __tablename__ = "daily_coaching_sessions"

    coaching_session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id             = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    session_completed = Column(Boolean, default=False)
    motivation_level  = Column(Integer, nullable=True)   # 1-10
    session_date      = Column(Date, nullable=True)
    greeting_message  = Column(Text, nullable=True)
    nutrition_message = Column(Text, nullable=True)

    user = relationship("User", back_populates="coaching_sessions")


# ══════════════════════════════════════════════════════════════════════════════
# MOTIVATION MESSAGES
# ══════════════════════════════════════════════════════════════════════════════

class MotivationMessage(Base):
    __tablename__ = "motivation_messages"

    message_id      = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    is_read         = Column(Boolean, default=False)
    send_date       = Column(DateTime(timezone=True), server_default=func.now())
    message_content = Column(Text, nullable=False)
    message_type    = Column(Enum(MessageTypeEnum), nullable=True)

    user = relationship("User", back_populates="motivation_messages")


# ══════════════════════════════════════════════════════════════════════════════
# DIET PLANS
# ══════════════════════════════════════════════════════════════════════════════

class DietPlan(Base):
    __tablename__ = "diet_plans"

    diet_plan_id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id               = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    daily_calories_target = Column(Float, nullable=True)
    carbs_target          = Column(Float, nullable=True)   # grams
    protein_target        = Column(Float, nullable=True)   # grams
    fat_target            = Column(Float, nullable=True)   # grams
    version               = Column(Integer, default=1)
    created_by            = Column(String(50), nullable=True)   # "AI" | "nutritionist"
    is_active             = Column(Boolean, default=True)
    created_at            = Column(DateTime(timezone=True), server_default=func.now())
    plan_name             = Column(String(200), nullable=False)

    user        = relationship("User",      back_populates="diet_plans")
    daily_meals = relationship("DailyMeal", back_populates="diet_plan", cascade="all, delete-orphan")


# ══════════════════════════════════════════════════════════════════════════════
# DAILY MEALS  (containing_meals → FK on this table)
# ══════════════════════════════════════════════════════════════════════════════

class DailyMeal(Base):
    __tablename__ = "daily_meals"

    daily_meal_id  = Column(Integer, primary_key=True, autoincrement=True)
    diet_plan_id   = Column(Integer, ForeignKey("diet_plans.diet_plan_id", ondelete="CASCADE"), nullable=False, index=True)
    total_calories = Column(Float, nullable=True)
    total_protein  = Column(Float, nullable=True)
    total_carb     = Column(Float, nullable=True)
    total_fats     = Column(Float, nullable=True)
    meal_order     = Column(Integer, nullable=True)
    meal_time      = Column(Time, nullable=True)
    day_of_week    = Column(String(20), nullable=True)   # "Monday" … "Sunday"

    diet_plan  = relationship("DietPlan",  back_populates="daily_meals")
    food_items = relationship("FoodItem",  back_populates="daily_meal", cascade="all, delete-orphan")


# ══════════════════════════════════════════════════════════════════════════════
# FOOD ITEMS  (containing_food → FK on this table)
# ══════════════════════════════════════════════════════════════════════════════

class FoodItem(Base):
    __tablename__ = "food_items"

    food_item_id  = Column(Integer, primary_key=True, autoincrement=True)
    daily_meal_id = Column(Integer, ForeignKey("daily_meals.daily_meal_id", ondelete="CASCADE"), nullable=False, index=True)

    calories   = Column(Float, nullable=True)
    protein    = Column(Float, nullable=True)
    carb       = Column(Float, nullable=True)
    fats       = Column(Float, nullable=True)
    is_eaten   = Column(Boolean, default=False)
    item_order = Column(Integer, nullable=True)
    grams      = Column(Float, nullable=True)
    food_name  = Column(String(200), nullable=False)

    daily_meal = relationship("DailyMeal", back_populates="food_items")


# ══════════════════════════════════════════════════════════════════════════════
# POPULATION INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════

class PopulationInsight(Base):
    __tablename__ = "population_insights"

    insight_id   = Column(Integer, primary_key=True, autoincrement=True)
    status       = Column(String(50), nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    category     = Column(String(100), nullable=True)
    insight_text = Column(Text, nullable=True)
    confidence   = Column(Float, nullable=True)   # 0.0 – 1.0

    users = relationship(
        "User",
        secondary=making_population,
        back_populates="population_insights",
    )


# ══════════════════════════════════════════════════════════════════════════════
# TRAINING JOBS  (background ML training tasks)
# ══════════════════════════════════════════════════════════════════════════════

class TrainingJob(Base):
    __tablename__ = "training_jobs"

    job_id        = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    started_at    = Column(DateTime(timezone=True), nullable=True)
    completed_at  = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    status        = Column(Enum(ExecutionStatusEnum), default=ExecutionStatusEnum.pending)

    user = relationship("User", back_populates="training_jobs")


# ══════════════════════════════════════════════════════════════════════════════
# STRATEGY PERFORMANCE  (tracks AI recommendation strategies)
# ══════════════════════════════════════════════════════════════════════════════

class StrategyPerformance(Base):
    __tablename__ = "strategy_performance"

    strategy_id      = Column(Integer, primary_key=True, autoincrement=True)
    user_id          = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)
    strategy_name    = Column(String(200), nullable=False)
    avg_improvement  = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    last_updated     = Column(DateTime(timezone=True), nullable=True)
    success_rate     = Column(Float, nullable=True)
    failures         = Column(Integer, default=0)
    successes        = Column(Integer, default=0)
    total_attempts   = Column(Integer, default=0)

    user = relationship("User", back_populates="strategy_performances")


# ══════════════════════════════════════════════════════════════════════════════
# PLAN ARCHIVES  (versioned snapshots of old workout / diet plans)
# ══════════════════════════════════════════════════════════════════════════════

class PlanArchive(Base):
    __tablename__ = "plan_archives"

    archive_id  = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    archived_at = Column(DateTime(timezone=True), server_default=func.now())
    plan_type   = Column(Enum(PlanTypeEnum), nullable=True)   # "workout" | "diet"
    reason      = Column(Text, nullable=True)

    # JSON — full snapshot of the plan at the time it was archived
    plan_data   = Column(JSONB, nullable=True)
    # e.g. { "plan_name": "...", "weekly_frequency": 4, "days": [...] }
    # stored as JSONB so it can be searched / queried without deserialisation

    user = relationship("User", back_populates="plan_archives")
