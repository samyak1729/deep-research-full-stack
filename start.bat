@echo off
REM Start script for Deep Research fullstack app (Windows)

setlocal enabledelayedexpansion

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo Please edit .env and add your API keys, then run this script again.
    exit /b 1
)

REM Load .env file
for /f "usebackq delims==" %%A in (.env) do (
    if not "%%A"=="" (
        set "%%A"
    )
)

REM Check if API keys are set
if "!OPENAI_API_KEY!"=="" (
    echo [ERROR] OPENAI_API_KEY not set in .env file
    exit /b 1
)

if "!TAVILY_API_KEY!"=="" (
    echo [ERROR] TAVILY_API_KEY not set in .env file
    exit /b 1
)

echo.
echo Starting Deep Research Fullstack App
echo.

REM Start backend in new window
echo Starting backend...
start "Deep Research Backend" /d "%cd%" python app/backend/main.py
timeout /t 2 /nobreak

REM Start frontend in new window
echo Starting frontend...
start "Deep Research Frontend" /d "%cd%" streamlit run app/frontend/app.py

timeout /t 3 /nobreak

echo.
echo All services started!
echo.
echo Access the application:
echo   Frontend: http://localhost:8501
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Close the command windows to stop the services.
echo.

pause
