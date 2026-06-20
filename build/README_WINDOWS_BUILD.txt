╔══════════════════════════════════════════════════════╗
║    DOC — Cómo generar el .exe en Windows            ║
╚══════════════════════════════════════════════════════╝

REQUISITOS:
- Windows 10/11 (64-bit)
- Python 3.12+ instalado
- Conexión a internet

PASOS (2 comandos):

1. Abrí cmd.exe como Administrador y ejecutá:

   pip install pyinstaller

2. Dentro de la carpeta donde está el código fuente, ejecutá:

   pyinstaller --onefile --name DOC.exe ^
     --add-data "frontend;frontend" ^
     --hidden-import uvicorn.logging ^
     --hidden-import uvicorn.loops.auto ^
     --hidden-import uvicorn.protocols.http.auto ^
     --strip ^
     --noupx ^
     --icon doc_logo.jpg ^
     src/main.py

3. El .exe aparece en la carpeta dist/

PARA CORRERLO:
   dist\DOC.exe
   → Abrir navegador en http://localhost:8080

NOTA: Windows Defender puede pedir confirmación la primera vez.
Es normal — es un servidor local legítimo.

¿PROBLEMAS?
- Si da error "python no encontrado": instalá Python desde python.org
- Si da error de permisos: ejecutá cmd como Administrador
