"""
DOC - System/Performance Tests
Tests: memory usage, CPU efficiency, disk footprint, data integrity
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import psutil
from pathlib import Path

from src.engine.savant import SavantEngine
from src.models.database import db
from src.config import CONFIG

class TestMemoryFootprint:
    """Ensure minimal RAM usage — 32-bit compatible"""
    
    def test_engine_init_memory(self):
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        
        engine = SavantEngine()
        
        mem_after = process.memory_info().rss
        increase = (mem_after - mem_before) / 1024 / 1024  # MB
        
        print(f"Engine init memory increase: {increase:.2f} MB")
        assert increase < 50, f"Engine uses too much memory: {increase:.2f} MB"
    
    def test_database_file_size(self):
        db_path = CONFIG.DB_PATH
        if db_path.exists():
            size_mb = db_path.stat().st_size / 1024 / 1024
            assert size_mb < 10, f"Database too large: {size_mb:.2f} MB"

class TestCPU:
    """CPU efficiency — no heavy computation"""
    
    def test_analysis_speed(self):
        engine = SavantEngine()
        
        times = []
        for _ in range(5):
            start = time.time()
            from src.models.database import PatientProfile
            patient = PatientProfile(identifier="cpu_test", id=1)
            engine.analyze_symptoms(patient, "Dolor de cabeza moderado, sensibilidad a la luz", [])
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg = sum(times) / len(times)
        print(f"Average analysis time: {avg*1000:.0f}ms")
        assert avg < 5.0, f"Analysis too slow: {avg:.2f}s"

class TestDataIntegrity:
    """No data loss — all patient data preserved"""
    
    def test_unicode_symptoms(self):
        engine = SavantEngine()
        from src.models.database import PatientProfile
        patient = PatientProfile(identifier="unicode_test", id=1)
        text = "Tengo dolor de cabeza con náuseas y vómitos. Me duele aquí: →"
        result = engine.analyze_symptoms(patient, text, [])
        assert result is not None
        assert isinstance(result.get("symptoms_parsed"), dict)
    
    def test_result_structure(self):
        engine = SavantEngine()
        from src.models.database import PatientProfile
        patient = PatientProfile(identifier="struct_test", id=1)
        result = engine.analyze_symptoms(patient, "Fiebre y tos", [])
        
        required_keys = ["symptoms_parsed", "red_flags", "analysis", "confidence", "urgency", "recommendation"]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
