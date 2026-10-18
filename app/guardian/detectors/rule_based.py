from typing import Any
from app.models.agent import AgentEvent


class RuleBasedDetector:
    """Layer 1: Fast, deterministic checks (<10ms) to catch obvious anomalies."""

    def __init__(self):
        pass

    def check_event_consistency(self, current_event: AgentEvent, previous_events: list[AgentEvent]) -> dict[str, Any]:
        """
        Returns a dict with:
        - is_anomaly: bool
        - reason: str
        - anomaly_type: str
        """
        if not previous_events:
            return {"is_anomaly": False, "reason": "", "anomaly_type": ""}

        # Check 1: Loop / Hallucination check (Same exact payload output repeatedly)
        same_output_count = 0
        for prev in previous_events:
            if prev.payload.get("response") == current_event.payload.get("response"):
                same_output_count += 1

        if same_output_count >= 3:
            return {
                "is_anomaly": True,
                "reason": "Agent repeated the exact same output 3 times. Possible stuck loop.",
                "anomaly_type": "hallucination_loop",
            }

        # Check 2: Error propagation in payload
        if "error" in current_event.payload:
            return {
                "is_anomaly": True,
                "reason": f"Agent encountered an error: {current_event.payload['error']}",
                "anomaly_type": "execution_error",
            }

        # Check 3: Out of order steps
        last_step = max(prev.step_number for prev in previous_events)
        if current_event.step_number <= last_step:
            return {
                "is_anomaly": True,
                "reason": f"Out of order step. Previous max: {last_step}, Current: {current_event.step_number}",
                "anomaly_type": "state_corruption",
            }

        return {"is_anomaly": False, "reason": "", "anomaly_type": ""}