from sqlalchemy.ext.asyncio import AsyncSession
from app.core import crud
from app.guardian.detectors.rule_based import RuleBasedDetector
from app.guardian.detectors.semantic import SemanticDetector
from app.schemas.agent import AgentEventCreate


class GuardianService:
    def __init__(self):
        self.rule_detector = RuleBasedDetector()
        self.semantic_detector = SemanticDetector()

    async def process_new_event(self, db: AsyncSession, event_data: AgentEventCreate):
        # 1. Fetch history
        previous_events = await crud.get_events_by_agent(db, event_data.agent_id)
        
        # 2. Save event
        new_event = await crud.create_event(
            db=db, agent_id=event_data.agent_id, step_number=event_data.step_number,
            event_type=event_data.event_type, payload=event_data.payload,
            tokens_used=event_data.tokens_used, cost_usd=event_data.cost_usd,
        )

        # 3. LAYER 1: Rule-Based Check (Fast)
        rule_result = self.rule_detector.check_event_consistency(new_event, previous_events)
        
        if rule_result["is_anomaly"]:
            return await self._trigger_rollback(db, event_data, new_event, rule_result, "Rule-Based")

        # 4. LAYER 2: Semantic Check (LLM)
        semantic_result = await self.semantic_detector.check_semantic_consistency(previous_events, new_event)
        
        if semantic_result["is_anomaly"]:
            return await self._trigger_rollback(db, event_data, new_event, semantic_result, "Semantic-AI")

        # 5. All Good
        return {"event": new_event, "anomaly_detected": False, "recovery_action": "none"}

    async def _trigger_rollback(self, db, event_data, new_event, result, layer_name):
        """Helper to handle rollback logic."""
        latest_checkpoint = await crud.get_latest_safe_checkpoint(db, event_data.agent_id)
        rollback_step = latest_checkpoint.step_number if latest_checkpoint else 0

        await crud.create_recovery(
            db=db, agent_id=event_data.agent_id, detection_step=event_data.step_number,
            rollback_to_step=rollback_step, anomaly_type=result["anomaly_type"],
            reason=result["reason"], cost_saved_usd=0.05, 
        )
        
        await crud.rollback_to_checkpoint(db, event_data.agent_id, rollback_step)
        
        print(f"🚨 [{layer_name}] ANOMALY DETECTED at step {event_data.step_number}: {result['reason']}")
        print(f"🔄 Rolled back to checkpoint step {rollback_step}")
        
        return {"event": new_event, "anomaly_detected": True, "recovery_action": "rollback"}