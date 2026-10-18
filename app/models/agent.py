import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AgentEvent(Base):
    """
    Every action an agent takes — LLM call, tool result, decision.
    Event-sourced: this is the source of truth.
    """
    __tablename__ = "agent_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    agent_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'llm_call', 'tool_result', 'decision'
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Numeric(10, 6), default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_agent_events_agent_step", "agent_id", "step_number"),
    )


class Checkpoint(Base):
    """
    Snapshot of agent state at a safe boundary.
    Used for rollback when anomaly is detected.
    """
    __tablename__ = "checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    agent_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    state_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_safe: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_checkpoints_agent_step", "agent_id", "step_number"),
    )


class CausalEdge(Base):
    """
    Dependency graph between agent steps.
    Step B depends on Step A → if A is rolled back, B must be too.
    """
    __tablename__ = "causal_graph"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    agent_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    from_step: Mapped[int] = mapped_column(Integer, nullable=False)
    to_step: Mapped[int] = mapped_column(Integer, nullable=False)
    dependency_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'data', 'decision', 'side_effect'
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_causal_agent_steps", "agent_id", "from_step", "to_step"),
    )


class RecoveryLog(Base):
    """
    Audit trail of all recovery operations.
    Proves SCORPGUARD did its job.
    """
    __tablename__ = "recovery_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    agent_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    detection_step: Mapped[int] = mapped_column(Integer, nullable=False)
    rollback_to_step: Mapped[int] = mapped_column(Integer, nullable=False)
    anomaly_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'hallucination', 'cost_breach', 'state_corruption'
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    cost_saved_usd: Mapped[float] = mapped_column(Numeric(10, 6), default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )