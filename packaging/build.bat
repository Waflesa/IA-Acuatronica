@echo off
setlocal
cd /d "%~dp0"

echo [1/2] Empaquetando con PyInstaller...
python build_app.py
if errorlevel 1 (
    echo ERROR: fallo PyInstaller.
    exit /b 1
)

set DISTDIR=%TEMP%\h2ob\dist\H2-OBSERVER
if not exist "%DISTDIR%\H2-OBSERVER.exe" (
    echo ERROR: no se encontro el exe en %DISTDIR%
    exit /b 1
)

echo [2/2] Generando instalador con Inno Setup...
set ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe
if not exist "%ISCC%" set ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
"%ISCC%" /DDistDir="%DISTDIR%" installer.iss
if errorlevel 1 (
    echo ERROR: fallo Inno Setup.
    exit /b 1
)

echo.
echo LISTO: dist\H2-OBSERVER-Setup.exe
endlocal