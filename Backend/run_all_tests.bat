@echo off
REM Run all backend tests with coverage

echo ========================================
echo Running AI Hairstyle Suggester Tests
echo ========================================
echo.

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Install test dependencies
echo Installing test dependencies...
pip install pytest pytest-cov pytest-mock -q

echo.
echo Running tests...
echo.

REM Run tests with coverage
python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term

echo.
echo ========================================
echo Tests completed!
echo Coverage report: backend/htmlcov/index.html
echo ========================================

pause
