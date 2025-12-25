@echo off
REM Quick test run without coverage

echo Running quick tests...

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run tests
python -m pytest tests/ -v --tb=short

pause
