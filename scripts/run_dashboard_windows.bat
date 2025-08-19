@echo off
REM IT Dashboard Generator - Windows Task Scheduler Script

echo Starting IT Dashboard Generator...
echo %date% %time%

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\\Scripts\\activate.bat" (
    echo Activating virtual environment...
    call venv\\Scripts\\activate.bat
)

REM Run the dashboard generator
echo Running dashboard generator...
python main.py --config config\\settings.json

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo Dashboard generation completed successfully
    echo %date% %time% - SUCCESS >> logs\\scheduler.log
) else (
    echo Dashboard generation failed with error code %ERRORLEVEL%
    echo %date% %time% - ERROR: Exit code %ERRORLEVEL% >> logs\\scheduler.log
)

echo Finished at %date% %time%
pause
