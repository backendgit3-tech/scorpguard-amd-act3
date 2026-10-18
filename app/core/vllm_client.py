import httpx
import json
import re
from openai import AsyncOpenAI
from app.core.config import settings

class VLLMClient:
    def __init__(self):
        self.base_url = settings.VLLM_BASE_URL
        self.model = "Qwen/Qwen2.5-7B-Instruct"
        
        # Ab key yahan hardcode nahi hai, .env se aa rahi hai
        self.groq_api_key = settings.GROQ_API_KEY 
        self.groq_model = "openai/gpt-oss-120b" 
        self.use_groq_fallback = True

    async def generate_verdict(self, previous_context: str, current_output: str) -> dict:
        system_prompt = """You are SCORPGUARD, an AI security auditor. 
        Analyze the Current Output against the Previous Context.
        If the Current Output contradicts the Previous Context, hallucinates, or contains logical errors, set 'is_anomaly' to true.
        You MUST respond in strict JSON format ONLY: {"is_anomaly": bool, "reason": "string"}"""

        user_prompt = f"Previous Context:\n{previous_context}\n\nCurrent Output:\n{current_output}"

        # AMD vLLM try karo
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.0, "max_tokens": 150
                    }
                )
                response.raise_for_status()
                return self._parse_llm_response(response.json()["choices"][0]["message"]["content"])
        except Exception as e:
            print(f"⚠️ [SCORPGUARD] AMD vLLM offline. Switching to Groq Fallback...")
            
            if self.use_groq_fallback and self.groq_api_key:
                try:
                    groq_client = AsyncOpenAI(
                        base_url="https://api.groq.com/openai/v1",
                        api_key=self.groq_api_key
                    )
                    response = await groq_client.chat.completions.create(
                        model=self.groq_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.0, max_tokens=150
                    )
                    print("✅ [SCORPGUARD] Groq Verdict received.")
                    return self._parse_llm_response(response.choices[0].message.content)
                except Exception as groq_error:
                    print(f"❌ [SCORPGUARD] Groq Fallback failed: {groq_error}")
                    return {"is_anomaly": False, "reason": "Groq Error"}
            
            return {"is_anomaly": False, "reason": "No API Key"}

    def _parse_llm_response(self, content: str) -> dict:
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try: return json.loads(json_match.group(0))
            except: pass
        return {"is_anomaly": False, "reason": "Parse error"}

vllm_client = VLLMClient()