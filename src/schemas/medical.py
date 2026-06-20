"""
DOC - Medical Data Schemas
Pydantic models with zero-overhead serialization
"""
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class PatientIn(BaseModel):
    identifier: str = Field(..., min_length=2, max_length=64, description="Unique patient identifier (hash-based)")
    age_group: Optional[str] = ""
    general_state: Optional[str] = ""
    allergies: Optional[str] = ""
    chronic_conditions: Optional[str] = ""

class SymptomIn(BaseModel):
    symptoms: str = Field(..., min_length=3, max_length=2000, description="Symptom description in natural language")
    patient_id: Optional[str] = ""
    follow_up: Optional[bool] = False
    consultation_id: Optional[int] = 0
    
    @field_validator("symptoms")
    @classmethod
    def sanitize(cls, v: str) -> str:
        return v.strip()[:2000]

class ConsultationOut(BaseModel):
    id: int
    patient_id: int
    symptoms_raw: str
    symptoms_parsed: str
    llm_depurated: str
    suggested_conditions: str
    red_flags: str
    confidence: float
    created_at: float

class TriageResponse(BaseModel):
    success: bool = True
    consultation_id: Optional[int] = None
    analysis: Dict[str, Any] = {}
    symptoms_parsed: Dict[str, Any] = {}
    red_flags: List[Dict[str, str]] = []
    suggested_questions: List[str] = []
    urgency: str = "non-urgent"
    recommendation: str = ""
    confidence: float = 0.0
    similar_cases: int = 0
    processing_time_s: float = 0.0
    disclaimer: str = "⚠️ ESTO NO ES UN DIAGNÓSTICO MÉDICO. Consulte siempre con un profesional de la salud."
    memory_stats: Dict[str, Any] = {}

class StatsResponse(BaseModel):
    patients: int = 0
    consultations: int = 0
    knowledge_entries: int = 0
    memory_cases: int = 0
    version: str = "1.0.0"
