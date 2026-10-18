from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import crud
from app.db.session import get_db
from app.schemas.agent import RecoveryCreate, RecoveryResponse

router = APIRouter()


@router.post("", response_model=RecoveryResponse, status_code=201)
async def create_recovery(
    recovery: RecoveryCreate, db: AsyncSession = Depends(get_db)
):
    """Log a recovery operation (audit trail for SCORPGUARD)."""
    return await crud.create_recovery(
        db=db,
        agent_id=recovery.agent_id,
        detection_step=recovery.detection_step,
        rollback_to_step=recovery.rollback_to_step,
        anomaly_type=recovery.anomaly_type,
        reason=recovery.reason,
        cost_saved_usd=recovery.cost_saved_usd,
    )


@router.get("/{agent_id}", response_model=list[RecoveryResponse])
async def get_agent_recoveries(
    agent_id: str, db: AsyncSession = Depends(get_db)
):
    """Get all recovery operations for an agent."""
    recoveries = await crud.get_recoveries_by_agent(db, agent_id)
    if not recoveries:
        raise HTTPException(
            status_code=404,
            detail=f"No recoveries found for agent '{agent_id}'",
        )
    return recoveries