from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import settings
from app.core.redis_client import close_redis, redis_client
from app.db.session import Base, engine
from app.models import agent  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🦂 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("🦂 Database tables ready.")
    yield
    print("🦂 SCORPGUARD shutting down...")
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Agent Runtime Guardian — Production-grade resilience for AI agents",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# API Routes
app.include_router(api_router, prefix="/api/v1")

# Frontend Dashboard Mount & Route
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def serve_dashboard():
    return FileResponse("app/static/index.html")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "scorpguard",
        "version": settings.APP_VERSION,
    }


@app.get("/health/db")
async def health_db():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
        return {"status": "healthy", "database": "postgresql", "result": value}
    except Exception as e:
        return {"status": "unhealthy", "database": "postgresql", "error": str(e)}


@app.get("/health/redis")
async def health_redis():
    try:
        pong = await redis_client.ping()
        return {"status": "healthy", "redis": "connected", "ping": pong}
    except Exception as e:
        return {"status": "unhealthy", "redis": "error", "error": str(e)}