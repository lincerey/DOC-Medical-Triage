"""
DOC - Integration Tests
Tests: full API lifecycle, database, engine pipeline
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.database import db, PatientProfile, Consultation

client = TestClient(app)

class TestAPIEndpoints:
    """Test full HTTP API lifecycle"""
    
    def test_health_endpoint(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "operational"
        assert data["engine"] == "savant"
    
    def test_triage_simple(self):
        resp = client.post("/api/v1/triage", json={
            "symptoms": "Dolor de cabeza leve desde ayer"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] == True
        assert "analysis" in data
        assert "urgency" in data
        assert "recommendation" in data
    
    def test_triage_with_red_flags(self):
        resp = client.post("/api/v1/triage", json={
            "symptoms": "Me duele mucho el pecho y no puedo respirar bien"
        })
        assert resp.status_code == 200
        data = resp.json()
        # Should detect high urgency
        assert data["urgency"] in ("emergency", "high")
    
    def test_triage_long_text(self):
        resp = client.post("/api/v1/triage", json={
            "symptoms": "Hace una semana empecé con dolor de garganta que luego se convirtió en tos seca. Ahora tengo fiebre de 38 grados, congestión nasal, y me duele todo el cuerpo. He estado tomando paracetamol pero no mejora."
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data.get("suggested_questions", [])) > 0
    
    def test_stats_endpoint(self):
        resp = client.get("/api/v1/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "patients" in data
        assert "consultations" in data
        assert "version" in data

class TestDatabase:
    """Test database operations"""
    
    def test_patient_crud(self):
        patient = db.get_or_create_patient("integration_test_user")
        assert patient.id is not None
        assert patient.identifier == "integration_test_user"
        
        patient.age_group = "adulto"
        patient.chronic_conditions = "hipertensión"
        db.update_patient(patient)
        
        patient2 = db.get_or_create_patient("integration_test_user")
        assert patient2.age_group == "adulto"
    
    def test_consultation_save(self):
        patient = db.get_or_create_patient("consult_test")
        cons = Consultation(
            patient_id=patient.id,
            symptoms_raw="Dolor de prueba",
            symptoms_parsed='{"test": true}',
            llm_depurated='{"result": "ok"}',
            confidence=0.85,
            tokens_used=100
        )
        cid = db.save_consultation(cons)
        assert cid > 0
        
        history = db.get_patient_history(patient.id)
        assert len(history) >= 1

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
