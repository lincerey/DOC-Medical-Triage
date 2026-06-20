"""
DOC - LLM Provider Adapter
Abstracted interface for any LLM backend (OpenAI, Anthropic, local)
"""
from __future__ import annotations
import json, time, hashlib, os
from typing import Optional, Dict, List, Any
from ..config import CONFIG

class LLMProvider:
    """Lightweight LLM wrapper — optimized for medical accuracy"""
    
    def __init__(self):
        self._config = CONFIG
        self._client = None
        self._base_url = self._config.LLM_API_BASE
    
    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Get completion with medical-grade system prompt"""
        if not self._config.LLM_API_KEY:
            return self._fallback_response(user_prompt)
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=self._config.LLM_TIMEOUT) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._config.LLM_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self._config.LLM_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": self._config.LLM_TEMPERATURE,
                        "max_tokens": self._config.LLM_MAX_TOKENS
                    }
                )
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            return self._fallback_response(user_prompt, error=str(e))
    
    def _fallback_response(self, user_prompt: str, error: str = "") -> str:
        """Fallback when LLM is unavailable — uses pattern matching"""
        from .savant import engine
        # Use the savant engine directly (no LLM needed)
        from ..models.database import db, PatientProfile, Consultation
        patient = db.get_or_create_patient(hashlib.md5(user_prompt.encode()).hexdigest()[:16])
        history = db.get_patient_history(patient.id)
        result = engine.analyze_symptoms(patient, user_prompt, history)
        
        return json.dumps(result, indent=2, ensure_ascii=False)

llm = LLMProvider()
