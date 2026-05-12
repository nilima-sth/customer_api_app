from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

from logger import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5433/customer_db"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        logger.debug("Database session opened.")
        yield db
    finally:
        db.close()
        logger.debug("Database session closed.")


def check_db_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully.")
    except Exception as exc:
        logger.error("Database connection FAILED: %s", exc)
