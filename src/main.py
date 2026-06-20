"""
DOC - Medical Intelligence System
Entry point — zero-compromise medical triage server
"""
from __future__ import annotations
import uvicorn, sys, os, json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from .config import CONFIG
from .api.routes import router
from .security.auth import security
from .models.database import db
from .engine.savant import SavantEngine

app = FastAPI(
    title="DOC — Medical Triage Assistant",
    description="Pre-consultation medical triage with savant-level diagnostic reasoning",
    version=CONFIG.APP_VERSION,
    docs_url="/docs",
    redoc_url=None
)

# CORS — hospital-network friendly
app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFIG.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router)

# Health check
@app.get("/health")
async def health():
    return {
        "status": "operational",
        "version": CONFIG.APP_VERSION,
        "engine": "savant",
        "memory_cases": 0
    }

# Frontend served from static
frontend_dir = Path(__file__).parent.parent / "frontend"
frontend_dir.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>DOC — Medical Intelligence</h1><p>Frontend not found</p>")

def main():
    """Entry point with optimized server config"""
    port = int(os.getenv("DOC_PORT", "8080"))
    host = os.getenv("DOC_HOST", "0.0.0.0")
    
    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║              DOC — Medical Intelligence          ║
    ║         Savant Diagnostic Engine v{CONFIG.APP_VERSION}         ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        workers=1,  # Single process for medical consistency
        loop="asyncio",
        http="httptools",
        limit_concurrency=100
    )

if __name__ == "__main__":
    main()
