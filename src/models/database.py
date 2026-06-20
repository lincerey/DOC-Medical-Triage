
"""
DOC - Database Engine - AI-optimized SQLite with memory-mapped IO
"""
from __future__ import annotations
import sqlite3, json, time, os, mmap, struct
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import threading

from ..config import CONFIG

@dataclass
class PatientProfile:
    id: Optional[int] = None
    identifier: str = ""
    age_group: str = ""
    general_state: str = ""
    allergies: str = ""
    chronic_conditions: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0

@dataclass
class Consultation:
    id: Optional[int] = None
    patient_id: int = 0
    symptoms_raw: str = ""
    symptoms_parsed: str = "{}"
    llm_raw_response: str = ""
    llm_depurated: str = ""
    llm_recursion_log: str = "[]"
    suggested_conditions: str = "[]"
    red_flags: str = "[]"
    confidence: float = 0.0
    patient_satisfaction: float = 0.0
    created_at: float = 0.0
    tokens_used: int = 0

@dataclass
class MedicalKnowledge:
    id: Optional[int] = None
    source: str = ""
    title: str = ""
    content_hash: str = ""
    embedding: bytes = b""
    tags: str = "[]"
    created_at: float = 0.0

class DocDatabase:
    __slots__ = ("_pool", "_lock", "_executor")
    
    def __init__(self):
        self._lock = threading.Lock()
        self._pool = []
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._init_db()
    
    def _init_db(self):
        conn = self._get_conn()
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=-8000")
            conn.execute("PRAGMA page_size=4096")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA mmap_size=268435456")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identifier TEXT UNIQUE NOT NULL,
                    age_group TEXT DEFAULT '',
                    general_state TEXT DEFAULT '',
                    allergies TEXT DEFAULT '',
                    chronic_conditions TEXT DEFAULT '',
                    created_at REAL DEFAULT (julianday('now')),
                    updated_at REAL DEFAULT (julianday('now'))
                );
                CREATE TABLE IF NOT EXISTS consultations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    symptoms_raw TEXT DEFAULT '',
                    symptoms_parsed TEXT DEFAULT '{}',
                    llm_raw_response TEXT DEFAULT '',
                    llm_depurated TEXT DEFAULT '',
                    llm_recursion_log TEXT DEFAULT '[]',
                    suggested_conditions TEXT DEFAULT '[]',
                    red_flags TEXT DEFAULT '[]',
                    confidence REAL DEFAULT 0.0,
                    patient_satisfaction REAL DEFAULT 0.0,
                    created_at REAL DEFAULT (julianday('now')),
                    tokens_used INTEGER DEFAULT 0,
                    FOREIGN KEY(patient_id) REFERENCES patients(id)
                );
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content_hash TEXT UNIQUE NOT NULL,
                    embedding BLOB DEFAULT NULL,
                    tags TEXT DEFAULT '[]',
                    created_at REAL DEFAULT (julianday('now'))
                );
                CREATE INDEX IF NOT EXISTS idx_patient_iden ON patients(identifier);
                CREATE INDEX IF NOT EXISTS idx_cons_patient ON consultations(patient_id);
                CREATE INDEX IF NOT EXISTS idx_cons_created ON consultations(created_at);
                CREATE INDEX IF NOT EXISTS idx_know_hash ON knowledge(content_hash);
            """)
            conn.commit()
        finally:
            self._release_conn(conn)
    
    def _get_conn(self):
        with self._lock:
            if self._pool:
                return self._pool.pop()
            conn = sqlite3.connect(str(CONFIG.DB_PATH), timeout=3.0, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA busy_timeout=3000")
            return conn
    
    def _release_conn(self, conn):
        with self._lock:
            if len(self._pool) < CONFIG.DB_POOL_SIZE:
                self._pool.append(conn)
            else:
                conn.close()
    
    @contextmanager
    def _cursor(self):
        conn = self._get_conn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._release_conn(conn)
    
    def get_or_create_patient(self, identifier: str) -> PatientProfile:
        with self._cursor() as conn:
            row = conn.execute("SELECT * FROM patients WHERE identifier = ?", (identifier,)).fetchone()
            if row:
                return PatientProfile(**dict(row))
            now = time.time()
            conn.execute(
                "INSERT INTO patients (identifier, created_at, updated_at) VALUES (?, ?, ?)",
                (identifier, now, now)
            )
            pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            return PatientProfile(id=pid, identifier=identifier, created_at=now, updated_at=now)
    
    def update_patient(self, patient: PatientProfile):
        with self._cursor() as conn:
            conn.execute(
                "UPDATE patients SET age_group=?, general_state=?, allergies=?, chronic_conditions=?, updated_at=? WHERE id=?",
                (patient.age_group, patient.general_state, patient.allergies,
                 patient.chronic_conditions, time.time(), patient.id)
            )
    
    def save_consultation(self, c: Consultation) -> int:
        with self._cursor() as conn:
            now = time.time()
            conn.execute(
                "INSERT INTO consultations (patient_id, symptoms_raw, symptoms_parsed, llm_raw_response, llm_depurated, llm_recursion_log, suggested_conditions, red_flags, confidence, patient_satisfaction, created_at, tokens_used) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (c.patient_id, c.symptoms_raw, c.symptoms_parsed,
                 c.llm_raw_response, c.llm_depurated, c.llm_recursion_log,
                 c.suggested_conditions, c.red_flags, c.confidence,
                 c.patient_satisfaction, now, c.tokens_used)
            )
            return conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    def get_patient_history(self, patient_id: int, limit: int = 20) -> List[Dict]:
        with self._cursor() as conn:
            rows = conn.execute(
                "SELECT * FROM consultations WHERE patient_id=? ORDER BY created_at DESC LIMIT ?",
                (patient_id, limit)
            ).fetchall()
            return [dict(r) for r in rows]
    
    def get_recent_consultations(self, limit: int = 50) -> List[Dict]:
        with self._cursor() as conn:
            rows = conn.execute(
                "SELECT * FROM consultations ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]
    
    def store_knowledge(self, k: MedicalKnowledge):
        with self._cursor() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO knowledge (source, title, content_hash, embedding, tags, created_at) VALUES (?,?,?,?,?,?)",
                (k.source, k.title, k.content_hash, k.embedding, k.tags, time.time())
            )
    
    def search_knowledge_by_tags(self, tags: List[str], limit: int = 10) -> List[Dict]:
        with self._cursor() as conn:
            like_clauses = " OR ".join(["tags LIKE ?"] * len(tags))
            params = [f"%{t}%" for t in tags]
            rows = conn.execute(
                f"SELECT * FROM knowledge WHERE {like_clauses} ORDER BY created_at DESC LIMIT ?",
                params + [limit]
            ).fetchall()
            return [dict(r) for r in rows]
    
    def get_stats(self) -> Dict:
        with self._cursor() as conn:
            patients = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
            consults = conn.execute("SELECT COUNT(*) FROM consultations").fetchone()[0]
            knowledge = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
            return {"patients": patients, "consultations": consults, "knowledge_entries": knowledge}

db = DocDatabase()
