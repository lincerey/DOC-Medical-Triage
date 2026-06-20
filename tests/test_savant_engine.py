"""
DOC - Savant Engine Unit Tests
Tests: hyperfocus parsing, red flag detection, recursive analysis, memory
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.engine.savant import SavantEngine, SavantMemoryStore
from src.models.database import PatientProfile, Consultation

@pytest.fixture
def engine():
    return SavantEngine()

class TestHyperfocusParse:
    """Test the savant hyperfocus symptom parser"""
    
    def test_time_patterns(self, engine):
        # Test duration detection
        result = engine._hyperfocus_parse("Tengo dolor desde hace 3 días")
        assert any("duracion_dias" in k for k in result)
        
        result = engine._hyperfocus_parse("Comenzó repentinamente hace una hora")
        assert any("duracion_horas" in k or "inicio_repentino" in k for k in result)
        
    def test_location_detection(self, engine):
        result = engine._hyperfocus_parse("Me duele la cabeza en la frente")
        assert result.get("ubicacion_cabeza", False) or "ubicacion_cabeza" in result
        
        result = engine._hyperfocus_parse("Dolor en el pecho")
        assert result.get("ubicacion_torax", False) or "ubicacion_torax" in result
    
    def test_intensity(self, engine):
        result = engine._hyperfocus_parse("El dolor es insoportable, del 8 al 10")
        assert any("intensidad_severa" in k or "intensidad_7_10" in k for k in result)
    
    def test_medical_signs(self, engine):
        result = engine._hyperfocus_parse("Tengo fiebre, tos con flema y dolor de garganta")
        key_str = str(result.keys())
        assert "sintoma_fiebre" in key_str or "sintoma_tos" in key_str
    
    def test_empty_input(self, engine):
        result = engine._hyperfocus_parse("")
        assert "_generic_query" in result or len(result) == 0

class TestRedFlagDetection:
    """Test emergency detection"""
    
    def test_emergency_flags(self, engine):
        result = engine._hyperfocus_parse("Me duele el pecho y no puedo respirar")
        flags = engine._detect_red_flags(result)
        assert len(flags) > 0
        assert flags[0]["urgency"] in ("emergency", "high")
    
    def test_high_priority(self, engine):
        result = engine._hyperfocus_parse("Tengo fiebre de 40 grados")
        flags = engine._detect_red_flags(result)
        assert len(flags) > 0
    
    def test_no_flags(self, engine):
        result = engine._hyperfocus_parse("Tengo una molestia leve en el brazo desde hace una semana")
        flags = engine._detect_red_flags(result)
        assert len(flags) == 0

class TestSavantMemory:
    """Test prodigious memory store"""
    
    def test_store_and_recall(self):
        memory = SavantMemoryStore()
        case = {"symptoms_parsed": {"ubicacion_cabeza": True, "sintoma_fiebre": True}, "analysis": {"possible_conditions": ["Migraña"]}}
        memory.store_case("abc123", case)
        assert memory.count() == 1
        
        results = memory.recall_similar({"ubicacion_cabeza": True})
        assert len(results) >= 1
    
    def test_similarity_search(self):
        memory = SavantMemoryStore()
        memory.store_case("a", {"symptoms_parsed": {"sintoma_fiebre": True, "sintoma_tos": True}})
        memory.store_case("b", {"symptoms_parsed": {"sintoma_dolor": True}})
        
        results = memory.recall_similar({"sintoma_fiebre": True, "sintoma_tos": True})
        assert len(results) >= 1

class TestRecursiveAnalysis:
    """Test full recursive diagnostic pipeline"""
    
    def test_full_pipeline(self, engine):
        patient = PatientProfile(identifier="test123", id=1)
        result = engine.analyze_symptoms(patient, "Dolor de cabeza leve desde ayer", [])
        assert "analysis" in result
        assert "confidence" in result
        assert "urgency" in result
        assert "recommendation" in result
    
    def test_recursion_depth(self, engine):
        patient = PatientProfile(identifier="test456", id=2)
        result = engine.analyze_symptoms(patient, "Tengo dolor abdominal severo, náuseas, vómitos y fiebre desde hace 2 días", [])
        depth = result.get("analysis", {}).get("recursion_depth", 0)
        assert depth >= 1
    
    def test_similar_cases_detected(self, engine):
        patient = PatientProfile(identifier="test789", id=3)
        result = engine.analyze_symptoms(patient, "Dolor de garganta y fiebre", [])
        # First analysis, similar should be 0 but analysis should complete
        assert result["similar_cases_found"] >= 0
    
    def test_gap_generation(self, engine):
        patient = PatientProfile(identifier="gap_test", id=4)
        result = engine.analyze_symptoms(patient, "Me duele", [])
        questions = result.get("analysis", {}).get("suggested_questions", [])
        assert len(questions) > 0

class TestScientificValidation:
    """Test scientific method validation"""
    
    def test_occams_razor(self, engine):
        hypothesis = {
            "possible_conditions": [
                {"name": "Cáncer", "confidence_bonus": 0.3},
                {"name": "Resfrío Común", "confidence_bonus": 0.8},
                {"name": "VIH", "confidence_bonus": 0.2},
                {"name": "Infección Leve", "confidence_bonus": 0.7},
            ],
            "reasoning": [],
            "scientific_basis": []
        }
        result = engine._scientific_validation(hypothesis)
        assert len(result["possible_conditions"]) <= 3

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
