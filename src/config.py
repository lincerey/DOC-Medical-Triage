"""
DOC - Medical Intelligence System
Configuration Module - Zero-compromise architecture
"""
from __future__ import annotations
import os, json, hashlib, hmac, time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class DocConfig:
    """Immutable configuration — single source of truth"""
    
    APP_NAME: str = "DOC"
    APP_VERSION: str = "1.0.0"
    BASE_DIR: Path = Path.home() / ".doc"
    DB_PATH: Path = BASE_DIR / "doc_core.db"
    KNOWLEDGE_DIR: Path = BASE_DIR / "knowledge"
    LOG_PATH: Path = BASE_DIR / "doc.log"
    MEMORY_PATH: Path = BASE_DIR / "memory_store"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.15
    LLM_MAX_TOKENS: int = 2048
    LLM_TIMEOUT: float = 30.0
    LLM_API_BASE: str = os.getenv("DOC_LLM_API_BASE", "https://api.openai.com/v1")
    LLM_API_KEY: str = os.getenv("DOC_LLM_API_KEY", "")
    SAVANT_RECURSION_DEPTH: int = 5
    SAVANT_MEMORY_TOP_K: int = 50
    SAVANT_HYPERFOCUS_THRESHOLD: float = 0.75
    SAVANT_SELF_CORRECT: bool = True
    SECRET_KEY: str = os.getenv("DOC_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    RATE_LIMIT_PER_MINUTE: int = 30
    ALLOWED_ORIGINS: tuple = ("*",)
    DB_POOL_SIZE: int = 2
    MAX_WORKERS: int = 4
    BINARY_MATH: bool = True

def init_dirs():
    c = DocConfig()
    c.BASE_DIR.mkdir(parents=True, exist_ok=True)
    c.KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    c.MEMORY_PATH.mkdir(parents=True, exist_ok=True)
    return c

CONFIG = init_dirs()
