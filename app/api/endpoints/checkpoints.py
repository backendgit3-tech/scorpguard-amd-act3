from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.core import crud
from app.db.session import get_db
from app.schemas.agent import CheckpointCreate, CheckpointResponse
from app.models.agent import AgentEvent

router = APIRouter()


@router.post("", response_model=CheckpointResponse, status_code=201)
async def create_checkpoint(
    checkpoint: CheckpointCreate, db: AsyncSession = Depends(get_db)
):
    """Save a checkpoint for an agent at a given step."""
    return await crud.create_checkpoint(
        db=db,
        agent_id=checkpoint.agent_id,
        step_number=checkpoint.step_number,
        state_snapshot=checkpoint.state_snapshot,
        is_safe=checkpoint.is_safe,
    )


@router.get("/{agent_id}/latest", response_model=CheckpointResponse)
async def get_latest_checkpoint(
    agent_id: str, db: AsyncSession = Depends(get_db)
):
    """Get the latest safe checkpoint for an agent (used for rollback)."""
    checkpoint = await crud.get_latest_safe_checkpoint(db, agent_id)
    if not checkpoint:
        raise HTTPException(
            status_code=404,
            detail=f"No safe checkpoint found for agent '{agent_id}'",
        )
    return checkpoint


@router.get("/{agent_id}/cost")
async def get_agent_cost(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Calculate total cost and tokens for an agent."""
    result = await db.execute(
        select(
            func.sum(AgentEvent.cost_usd).label("total_cost"),
            func.sum(AgentEvent.tokens_used).label("total_tokens")
        ).where(AgentEvent.agent_id == agent_id)
    )
    row = result.first()
    return {
        "agent_id": agent_id,
        "total_cost_usd": float(row.total_cost or 0.0),
        "total_tokens": int(row.total_tokens or 0)
    }