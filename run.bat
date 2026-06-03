@echo off
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python n'est pas installe. Tentative d'installation...
    winget install -e --id Python.Python.3.12 --scope machine
    echo.
    echo [IMPORTANT] Python a ete installe. 
    echo Fermez cette fenetre et relancez le fichier 'run.bat'.
    pause
    exit
)
echo Installation/Verification des dependances...
pip install -r requirements.txt --quiet
echo Lancement du programme...
python -m artlist_extractor.cli
pause