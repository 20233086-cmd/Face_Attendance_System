from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency FastAPI: mở session DB cho 1 request, tự đóng khi xong."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
