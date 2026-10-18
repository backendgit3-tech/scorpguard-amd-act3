from fastapi import APIRouter

from app.api.endpoints import events, checkpoints, recoveries

api_router = APIRouter()

api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(
    checkpoints.router, prefix="/checkpoints", tags=["checkpoints"]
)
api_router.include_router(
    recoveries.router, prefix="/recoveries", tags=["recoveries"]
)


@api_router.get("/")
async def api_root():
    return {"message": "SCORPGUARD API v1", "status": "operational"}