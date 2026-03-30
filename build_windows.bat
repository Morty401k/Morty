@echo off
:: build_windows.bat - Compila SimulatoreAudit.exe su Windows
:: Esegui come Amministratore per risultati migliori

echo.
echo   ================================================
echo     Build - Simulatore di Audit per Windows
echo   ================================================
echo.

:: Controlla Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] Python non trovato. Installalo da https://python.org
    pause
    exit /b 1
)

echo [OK] Python trovato.

:: Installa dipendenze
echo [*] Installazione dipendenze...
pip install pyinstaller fpdf2 paramiko -q

if %errorlevel% neq 0 (
    echo [ERRORE] Installazione dipendenze fallita.
    pause
    exit /b 1
)

echo [OK] Dipendenze installate.

:: Crea cartella output
if not exist "dist" mkdir dist

:: Compila
echo [*] Compilazione in corso (qualche minuto)...
pyinstaller --onefile ^
            --name "SimulatoreAudit" ^
            --hidden-import fpdf ^
            --hidden-import paramiko ^
            --hidden-import scapy ^
            --icon NONE ^
            avvia.py

if %errorlevel% neq 0 (
    echo [ERRORE] Compilazione fallita.
    pause
    exit /b 1
)

:: Pulizia
rmdir /s /q build
del SimulatoreAudit.spec

echo.
echo   ================================================
echo   Compilazione completata!
echo   Eseguibile: dist\SimulatoreAudit.exe
echo.
echo   Per avviarlo: tasto destro - Esegui come amministratore
echo   ================================================
echo.
pause
