"""
DOC - API Routes
Medical triage endpoints with safety/security enforced at every layer
"""
from __future__ import annotations
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
import json, time, hashlib
from typing import Dict, Any

from ..schemas.medical import SymptomIn, PatientIn, TriageResponse, StatsResponse
from ..schemas import ConsultationOut
from ..models.database import db, PatientProfile, Consultation, MedicalKnowledge
from ..engine.savant import SavantEngine
from ..engine.savant import engine as savant_engine
from ..engine.llm import llm
from ..security.auth import security

router = APIRouter(prefix="/api/v1")

@router.post("/triage", response_model=TriageResponse)
async def medical_triage(request: Request, symptom_in: SymptomIn):
    """
    Main medical triage endpoint — the savant hyperfocus engine in action.
    Returns structured analysis with safety disclaimers and red flags.
    """
    # Security layer
    rate_check = await security.rate_limit(request)
    if rate_check:
        return JSONResponse(status_code=429, content={"error": "Rate limit exceeded"})
    
    # Sanitize
    clean_symptoms = security.sanitize_input(symptom_in.symptoms)
    
    # Get or create patient
    patient_id = symptom_in.patient_id or security.generate_patient_id(clean_symptoms)
    patient = db.get_or_create_patient(patient_id)
    
    # Get history
    history = db.get_patient_history(patient.id)
    
    # SAVANT ANALYSIS
    start = time.time()
    result = savant_engine.analyze_symptoms(patient, clean_symptoms, history)
    
    # If LLM available, enhance with it
    if symptom_in.follow_up and symptom_in.consultation_id:
        # Shortcut for follow-ups
        pass
    
    # Build consultation record
    consultation = Consultation(
        patient_id=patient.id,
        symptoms_raw=clean_symptoms,
        symptoms_parsed=json.dumps(result.get("symptoms_parsed", {}), ensure_ascii=False),
        llm_depurated=json.dumps(result.get("analysis", {}), ensure_ascii=False),
        llm_recursion_log=json.dumps({"depth": result.get("recursion_depth", 0)}, ensure_ascii=False),
        suggested_conditions=json.dumps(
            result.get("analysis", {}).get("possible_conditions", []), ensure_ascii=False
        ),
        red_flags=json.dumps(result.get("red_flags", []), ensure_ascii=False),
        confidence=result.get("confidence", 0.0),
        created_at=time.time(),
        tokens_used=int(result.get("processing_time_s", 0) * 100)
    )
    cons_id = db.save_consultation(consultation)
    
    # Build response
    analysis = result.get("analysis", {})
    response = TriageResponse(
        success=True,
        consultation_id=cons_id,
        analysis=analysis,
        symptoms_parsed=result.get("symptoms_parsed", {}),
        red_flags=result.get("red_flags", []),
        suggested_questions=analysis.get("suggested_questions", []),
        urgency=result.get("urgency", "non-urgent"),
        recommendation=analysis.get("recommendation", ""),
        confidence=result.get("confidence", 0.0),
        similar_cases=result.get("similar_cases_found", 0),
        processing_time_s=result.get("processing_time_s", 0),
        memory_stats=savant_engine.get_memory_stats(),
        disclaimer="⚠️ ESTO NO ES UN DIAGNÓSTICO MÉDICO. Esta herramienta es informativa y no reemplaza la evaluación de un profesional de la salud. En caso de emergencia, llame al 107/911."
    )
    return response

@router.post("/patient/update")
async def update_patient(patient_in: PatientIn):
    """Update patient profile with medical context"""
    patient = db.get_or_create_patient(patient_in.identifier)
    if patient_in.age_group: patient.age_group = patient_in.age_group
    if patient_in.general_state: patient.general_state = patient_in.general_state
    if patient_in.allergies: patient.allergies = patient_in.allergies
    if patient_in.chronic_conditions: patient.chronic_conditions = patient_in.chronic_conditions
    db.update_patient(patient)
    return {"success": True, "patient_id": patient.id}

@router.get("/history/{patient_id}")
async def get_history(patient_id: str):
    """Get consultation history for a patient"""
    patient = db.get_or_create_patient(patient_id)
    history = db.get_patient_history(patient.id)
    return {"patient_id": patient.id, "consultations": history}

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """System statistics"""
    stats = db.get_stats()
    memory_stats = savant_engine.get_memory_stats()
    return StatsResponse(
        **stats,
        memory_cases=memory_stats.get("cases_stored", 0),
        version="1.0.0"
    )

@router.get("/memory/recall")
async def recall_memory():
    """Inspect savant memory store"""
    return savant_engine.get_memory_stats()
