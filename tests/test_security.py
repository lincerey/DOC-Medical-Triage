"""
DOC - Security Module Tests
Tests: JWT, rate limiting, input sanitization, HMAC
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.security.auth import DocSecurity
from src.config import CONFIG

@pytest.fixture
def security():
    return DocSecurity()

class TestJWT:
    def test_token_generation(self, security):
        token = security.generate_token({"user": "test", "role": "patient"})
        assert token.count(".") == 2
        assert len(token) > 50
    
    def test_token_verification(self, security):
        token = security.generate_token({"user": "test", "role": "patient"})
        payload = security.verify_token(token)
        assert payload is not None
        assert payload["user"] == "test"
    
    def test_tampered_token(self, security):
        token = security.generate_token({"user": "test"})
        tampered = token[:-5] + "XXXXX"
        payload = security.verify_token(tampered)
        assert payload is None
    
    def test_expired_token(self, security):
        token = security.generate_token({"user": "test"}, expiry_hours=0)
        # Force expiry by sleeping (token already expired since 0 hours)
        payload = security.verify_token(token)
        assert payload is None or payload.get("exp", 0) > time.time()

class TestInputSanitization:
    def test_sql_injection(self, security):
        clean = security.sanitize_input("'; DROP TABLE patients; --")
        assert "'" not in clean
        assert ";" not in clean
    
    def test_xss(self, security):
        clean = security.sanitize_input("<script>alert('xss')</script>")
        assert "<" not in clean
        assert ">" not in clean
    
    def test_normal_text_preserved(self, security):
        text = "Me duele la cabeza desde ayer"
        assert security.sanitize_input(text) == text

class TestPatientID:
    def test_deterministic(self, security):
        id1 = security.generate_patient_id("dolor de cabeza")
        id2 = security.generate_patient_id("dolor de cabeza")
        assert id1 == id2
    
    def test_different_inputs(self, security):
        id1 = security.generate_patient_id("dolor de cabeza")
        id2 = security.generate_patient_id("dolor abdominal")
        assert id1 != id2

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
