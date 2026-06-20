@echo off
title DOC — Instalador Automatico para Windows
color 0B
echo ====================================================
echo       DOC — Medical Triage Assistant Installer
echo ====================================================
echo.
echo [*] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python no encontrado. Abriendo web de descarga...
    start https://www.python.org/downloads/
    echo.
    echo     Descarga Python 3.12+ y EJECUTA ESTE INSTALADOR DE NUEVO.
    echo     IMPORTANTE: al instalar Python, tilda "Add Python to PATH"
    pause
    exit /b 1
)
echo     Python detectado correctamente.
echo.

echo [*] Instalando dependencias...
pip install --quiet --upgrade pip
pip install --quiet pyinstaller fastapi uvicorn pydantic sqlalchemy aiosqlite httpx pyjwt cryptography python-multipart aiofiles loguru psutil
echo     Dependencias instaladas.
echo.

echo [*] Compilando DOC.exe...
pyinstaller --onefile --name DOC ^
  --add-data "frontend;frontend" ^
  --hidden-import uvicorn.logging ^
  --hidden-import uvicorn.loops.auto ^
  --hidden-import uvicorn.protocols.http.auto ^
  --strip ^
  --noupx ^
  src/main.py

echo [*] Instalando en el sistema...
if not exist "%PROGRAMFILES%\DOC" mkdir "%PROGRAMFILES%\DOC"
copy /Y "dist\DOC.exe" "%PROGRAMFILES%\DOC\DOC.exe"

echo [*] Creando acceso directo en Escritorio...
set SCRIPT="%TEMP%\create_shortcut.vbs"
echo Set WshShell = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\DOC.lnk") >> %SCRIPT%
echo Shortcut.TargetPath = "%PROGRAMFILES%\DOC\DOC.exe" >> %SCRIPT%
echo Shortcut.WorkingDirectory = "%PROGRAMFILES%\DOC" >> %SCRIPT%
echo Shortcut.Description = "DOC — Asistente de Triage Medico" >> %SCRIPT%
echo Shortcut.IconLocation = "%PROGRAMFILES%\DOC\DOC.exe, 0" >> %SCRIPT%
echo Shortcut.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

echo [*] Creando acceso en Menu Inicio...
set SCRIPT="%TEMP%\create_startmenu.vbs"
echo Set WshShell = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo Set Shortcut = WshShell.CreateShortcut("%APPDATA%\Microsoft\Windows\Start Menu\Programs\DOC.lnk") >> %SCRIPT%
echo Shortcut.TargetPath = "%PROGRAMFILES%\DOC\DOC.exe" >> %SCRIPT%
echo Shortcut.WorkingDirectory = "%PROGRAMFILES%\DOC" >> %SCRIPT%
echo Shortcut.Description = "DOC — Asistente de Triage Medico" >> %SCRIPT%
echo Shortcut.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

echo [*] Creando desinstalador...
echo @echo off > "%PROGRAMFILES%\DOC\uninstall.bat"
echo echo Desinstalando DOC... >> "%PROGRAMFILES%\DOC\uninstall.bat"
echo timeout /t 2 /nobreak ^>nul >> "%PROGRAMFILES%\DOC\uninstall.bat"
echo rmdir /S /Q "%PROGRAMFILES%\DOC" >> "%PROGRAMFILES%\DOC\uninstall.bat"
echo del "%USERPROFILE%\Desktop\DOC.lnk" >> "%PROGRAMFILES%\DOC\uninstall.bat"
echo del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\DOC.lnk" >> "%PROGRAMFILES%\DOC\uninstall.bat"
echo echo DOC desinstalado correctamente. >> "%PROGRAMFILES%\DOC\uninstall.bat"
echo pause >> "%PROGRAMFILES%\DOC\uninstall.bat"

echo ====================================================
echo       INSTALACION COMPLETADA CON EXITO
echo ====================================================
echo.
echo   DOC.exe instalado en: %PROGRAMFILES%\DOC\
echo   Acceso directo: Escritorio ^> DOC
echo   Menu Inicio: DOC
echo   Desinstalador: %PROGRAMFILES%\DOC\uninstall.bat
echo.
echo   Para ejecutar DOC:
echo     Haga doble click en el icono del escritorio
echo     Abra http://localhost:8080 en su navegador
echo.
pause
