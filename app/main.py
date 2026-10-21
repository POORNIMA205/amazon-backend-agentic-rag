"""
Application entry point.
Run with: uvicorn app.main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401  (import so tables are registered before create_all)
from app.exceptions.handlers import register_exception_handlers
from app.logger import get_logger

from app.routers import auth, products, cart, orders, payment
from app.agentic_rag.router import router as agentic_rag_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if they don't exist yet.
    # For production, use Alembic migrations instead of create_all.
    Base.metadata.create_all(bind=engine)
    logger.info(f"{settings.APP_NAME} started in '{settings.ENV}' mode.")
    yield
    logger.info(f"{settings.APP_NAME} shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Amazon-style shopping backend with JWT authentication, Nginx-ready deployment, and a simple tool-routing RAG assistant.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - tighten allow_origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payment.router)
app.include_router(agentic_rag_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
