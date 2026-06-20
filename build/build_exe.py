"""
DOC - Cross-platform build script
Generates: .exe (Windows) | .app (macOS) | binary (Linux)
Optimizations: single-file, low memory, binary math
"""
from __future__ import annotations
import sys, os, platform, subprocess, shutil
from pathlib import Path

SYSTEM = platform.system()
BUILD_DIR = Path(__file__).parent
ROOT = BUILD_DIR.parent
DIST_DIR = ROOT / "dist"

def build_windows():
    print("[DOC BUILD] Building for Windows (exe)...")
    subprocess.run([
        "pyinstaller", "--clean", "--onefile",
        "--name", "DOC",
        "--distpath", str(DIST_DIR),
        "--add-data", f"{ROOT/'frontend'}:frontend",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--strip",
        "--noupx",
        str(ROOT / "src" / "main.py")
    ], check=True)
    exe_path = DIST_DIR / "DOC.exe"
    print(f"[DOC BUILD] ✅ Windows build: {exe_path}")

def build_macos():
    print("[DOC BUILD] Building for macOS (app)...")
    subprocess.run([
        "pyinstaller", "--clean", "--onefile",
        "--name", "DOC",
        "--distpath", str(DIST_DIR),
        "--add-data", f"{ROOT/'frontend'}:frontend",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--target-architecture", "arm64",
        "--osx-bundle-identifier", "org.doc.medical",
        str(ROOT / "src" / "main.py")
    ], check=True)
    app_path = DIST_DIR / "DOC"
    print(f"[DOC BUILD] ✅ macOS build: {app_path}")

def build_linux():
    print("[DOC BUILD] Building for Linux (binary)...")
    subprocess.run([
        "pyinstaller", "--clean", "--onefile",
        "--name", "doc",
        "--distpath", str(DIST_DIR),
        "--add-data", f"{ROOT/'frontend'}:frontend",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--strip",
        "--noupx",
        str(ROOT / "src" / "main.py")
    ], check=True)
    bin_path = DIST_DIR / "doc"
    print(f"[DOC BUILD] ✅ Linux build: {bin_path}")

def build():
    print("╔═══════════════════════════════════════╗")
    print("║   DOC — Cross-Platform Build System   ║")
    print("╚═══════════════════════════════════════╝")
    
    DIST_DIR.mkdir(exist_ok=True)
    
    if SYSTEM == "Windows":
        build_windows()
    elif SYSTEM == "Darwin":
        build_macos()
    else:
        build_linux()
    
    # Copy frontend to dist
    shutil.copytree(ROOT / "frontend", DIST_DIR / "frontend", dirs_exist_ok=True)
    
    print(f"\n[DOC BUILD] ✅ All builds complete. Artifacts in: {DIST_DIR}")

if __name__ == "__main__":
    build()
