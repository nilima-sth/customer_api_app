from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import check_db_connection
from router import router
from logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    check_db_connection()
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title="Customer API",
    description="4-Layer Clean Architecture | Twelve-Factor App",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)
