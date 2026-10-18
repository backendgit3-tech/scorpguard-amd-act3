import uuid
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import AgentEvent, Checkpoint, RecoveryLog


# ============ EVENT CRUD ============

async def create_event(
    db: AsyncSession,
    agent_id: str,
    step_number: int,
    event_type: str,
    payload: dict,
    tokens_used: int = 0,
    cost_usd: float = 0.0,
) -> AgentEvent:
    event = AgentEvent(
        agent_id=agent_id,
        step_number=step_number,
        event_type=event_type,
        payload=payload,
        tokens_used=tokens_used,
        cost_usd=cost_usd,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def get_events_by_agent(
    db: AsyncSession, agent_id: str, limit: int = 100
) -> list[AgentEvent]:
    result = await db.execute(
        select(AgentEvent)
        .where(AgentEvent.agent_id == agent_id)
        .order_by(AgentEvent.step_number)
        .limit(limit)
    )
    return list(result.scalars().all())


# ============ CHECKPOINT CRUD ============

async def create_checkpoint(
    db: AsyncSession,
    agent_id: str,
    step_number: int,
    state_snapshot: dict,
    is_safe: bool = True,
) -> Checkpoint:
    checkpoint = Checkpoint(
        agent_id=agent_id,
        step_number=step_number,
        state_snapshot=state_snapshot,
        is_safe=is_safe,
    )
    db.add(checkpoint)
    await db.commit()
    await db.refresh(checkpoint)
    return checkpoint


async def get_latest_safe_checkpoint(
    db: AsyncSession, agent_id: str
) -> Optional[Checkpoint]:
    result = await db.execute(
        select(Checkpoint)
        .where(Checkpoint.agent_id == agent_id)
        .where(Checkpoint.is_safe == True)  # noqa: E712
        .order_by(desc(Checkpoint.step_number))
        .limit(1)
    )
    return result.scalar_one_or_none()


# ============ RECOVERY CRUD ============

async def create_recovery(
    db: AsyncSession,
    agent_id: str,
    detection_step: int,
    rollback_to_step: int,
    anomaly_type: str,
    reason: str,
    cost_saved_usd: float = 0.0,
) -> RecoveryLog:
    recovery = RecoveryLog(
        agent_id=agent_id,
        detection_step=detection_step,
        rollback_to_step=rollback_to_step,
        anomaly_type=anomaly_type,
        reason=reason,
        cost_saved_usd=cost_saved_usd,
    )
    db.add(recovery)
    await db.commit()
    await db.refresh(recovery)
    return recovery


async def get_recoveries_by_agent(
    db: AsyncSession, agent_id: str
) -> list[RecoveryLog]:
    result = await db.execute(
        select(RecoveryLog)
        .where(RecoveryLog.agent_id == agent_id)
        .order_by(RecoveryLog.created_at)
    )
    return list(result.scalars().all())
async def rollback_to_checkpoint(
    db: AsyncSession, agent_id: str, checkpoint_step: int
) -> bool:
    """Delete all events that happened AFTER the safe checkpoint."""
    # Note: In a real system, we'd reverse side effects. 
    # Here, we delete future events to restore state.
    from sqlalchemy import delete
    
    await db.execute(
        delete(AgentEvent)
        .where(AgentEvent.agent_id == agent_id)
        .where(AgentEvent.step_number > checkpoint_step)
    )
    await db.commit()
    return True
async def rollback_to_checkpoint(
    db: AsyncSession, agent_id: str, checkpoint_step: int
) -> bool:
    """Delete all events that happened AFTER the safe checkpoint to restore state."""
    from sqlalchemy import delete
    
    await db.execute(
        delete(AgentEvent)
        .where(AgentEvent.agent_id == agent_id)
        .where(AgentEvent.step_number > checkpoint_step)
    )
    await db.commit()
    return True