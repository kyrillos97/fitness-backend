from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ──────────────────────────────────────────────
# Database URL — set DATABASE_URL in your .env
# Example: postgresql://user:password@localhost:5432/fitness_db
# ──────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/fitness_db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # Reconnect on stale connections
    pool_size=10,                # Max persistent connections
    max_overflow=20,             # Extra connections under load
    echo=False,                  # Set True to log SQL queries (dev only)
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


# ──────────────────────────────────────────────
# Dependency — use in FastAPI route functions
# ──────────────────────────────────────────────
def get_db():
    """Yield a database session and ensure it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database (call once on startup)."""
    from models import Base  # noqa: F401 — import registers all models
    Base.metadata.create_all(bind=engine)
