from app.core.vllm_client import vllm_client

class SemanticDetector:
    """Layer 2: LLM-based deep verification (Runs on AMD MI300X)."""

    async def check_semantic_consistency(self, previous_events: list, current_event) -> dict:
        if not previous_events:
            return {"is_anomaly": False, "reason": "", "anomaly_type": ""}

        # Pichle 3 events ka summary banayenge context ke liye
        previous_context = "\n".join([
            f"Step {e.step_number}: {e.payload.get('response', 'No response')}" 
            for e in previous_events[-3:]
        ])
        
        current_output = current_event.payload.get('response', '')

        verdict = await vllm_client.generate_verdict(previous_context, current_output)

        if verdict.get("is_anomaly"):
            return {
                "is_anomaly": True,
                "reason": f"LLM Verdict: {verdict.get('reason')}",
                "anomaly_type": "semantic_hallucination"
            }

        return {"is_anomaly": False, "reason": "", "anomaly_type": ""}