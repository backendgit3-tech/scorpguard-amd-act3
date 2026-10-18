import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============ EVENT SCHEMAS ============

class AgentEventCreate(BaseModel):
    """Payload to log a new agent event."""
    agent_id: str = Field(..., min_length=1, max_length=255)
    step_number: int = Field(..., ge=0)
    event_type: str = Field(
        ..., description="'llm_call', 'tool_result', 'decision'"
    )
    payload: dict[str, Any]
    tokens_used: int = Field(default=0, ge=0)
    cost_usd: float = Field(default=0.0, ge=0)


class AgentEventResponse(BaseModel):
    """Response shape for an agent event."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_id: str
    step_number: int
    event_type: str
    payload: dict[str, Any]
    tokens_used: int
    cost_usd: float
    created_at: datetime


# ============ CHECKPOINT SCHEMAS ============

class CheckpointCreate(BaseModel):
    """Payload to create a checkpoint."""
    agent_id: str = Field(..., min_length=1, max_length=255)
    step_number: int = Field(..., ge=0)
    state_snapshot: dict[str, Any]
    is_safe: bool = True


class CheckpointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_id: str
    step_number: int
    state_snapshot: dict[str, Any]
    is_safe: bool
    created_at: datetime


# ============ RECOVERY SCHEMAS ============

class RecoveryCreate(BaseModel):
    """Payload to log a recovery operation."""
    agent_id: str = Field(..., min_length=1, max_length=255)
    detection_step: int = Field(..., ge=0)
    rollback_to_step: int = Field(..., ge=0)
    anomaly_type: str = Field(
        ..., description="'hallucination', 'cost_breach', 'state_corruption'"
    )
    reason: str = Field(..., min_length=1)
    cost_saved_usd: float = Field(default=0.0, ge=0)


class RecoveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_id: str
    detection_step: int
    rollback_to_step: int
    anomaly_type: str
    reason: str
    cost_saved_usd: float
    created_at: datetime