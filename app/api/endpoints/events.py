from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import crud
from app.db.session import get_db
from app.schemas.agent import AgentEventCreate, AgentEventResponse
from app.guardian.service import GuardianService

router = APIRouter()
guardian = GuardianService()


@router.post("", response_model=dict, status_code=201)
async def create_event(
    event: AgentEventCreate, db: AsyncSession = Depends(get_db)
):
    """Log a new agent event and let SCORPGUARD check for anomalies."""
    result = await guardian.process_new_event(db, event)
    return {
        "event": AgentEventResponse.model_validate(result["event"]),
        "anomaly_detected": result["anomaly_detected"],
        "recovery_action": result["recovery_action"]
    }


@router.get("/{agent_id}", response_model=list[AgentEventResponse])
async def get_agent_events(
    agent_id: str, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get all events for an agent, ordered by step number."""
    events = await crud.get_events_by_agent(db, agent_id, limit)
    if not events:
        raise HTTPException(
            status_code=404, detail=f"No events found for agent '{agent_id}'"
        )
    return events