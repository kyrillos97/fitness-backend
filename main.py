from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("✅  Database tables created / verified.")
    yield

app = FastAPI(title="Fitness AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import users, diet, workout, progress

app.include_router(users.router,    prefix="/users",    tags=["Users"])
app.include_router(diet.router,     prefix="/diet",     tags=["Diet"])
app.include_router(workout.router,  prefix="/workout",  tags=["Workout"])
app.include_router(progress.router, prefix="/progress", tags=["Progress"])

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Fitness AI API is running 🚀"}