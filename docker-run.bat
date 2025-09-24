@echo off
REM Face Recognition Docker Runner for Windows
REM Compatible with Windows Command Prompt and PowerShell

echo 🚀 Starting Face Recognition Application with Docker...

REM Create necessary directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose version >nul 2>&1
if not errorlevel 1 (
    set COMPOSE_CMD=docker-compose
    goto :found_compose
)

docker compose version >nul 2>&1
if not errorlevel 1 (
    set COMPOSE_CMD=docker compose
    goto :found_compose
)

echo ❌ Docker Compose is not available. Please install Docker Compose.
pause
exit /b 1

:found_compose
echo 🔧 Using: %COMPOSE_CMD%

REM Build and start the application
echo 🔨 Building Docker image...
%COMPOSE_CMD% build --no-cache
if errorlevel 1 (
    echo ❌ Failed to build Docker image
    pause
    exit /b 1
)

echo 🚀 Starting application...
%COMPOSE_CMD% up -d
if errorlevel 1 (
    echo ❌ Failed to start application
    pause
    exit /b 1
)

echo ✅ Application started successfully!
echo.
echo 📋 Service Information:
echo    🌐 Application: http://localhost:5000
echo    📊 Health Check: http://localhost:5000/health
echo    📚 API Docs: See README.md
echo.
echo 📝 Logs:
echo    View logs: %COMPOSE_CMD% logs -f
echo    App logs only: %COMPOSE_CMD% logs -f face-recognition-app
echo.
echo 🛠️ Management:
echo    Stop: %COMPOSE_CMD% down
echo    Restart: %COMPOSE_CMD% restart
echo    Rebuild: %COMPOSE_CMD% up --build
echo.

REM Wait for application to be healthy
echo ⏳ Waiting for application to be ready...
for /l %%i in (1,1,30) do (
    curl -f http://localhost:5000/health >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Application is ready!
        goto :app_ready
    )
    echo    Attempt %%i/30: Waiting...
    timeout /t 2 >nul
)

:app_ready
REM Check if app is running
curl -f http://localhost:5000/health >nul 2>&1
if not errorlevel 1 (
    echo.
    echo 🎉 Face Recognition Service is now running!
    echo    Test it: curl http://localhost:5000/health
) else (
    echo.
    echo ⚠️  Application may not be fully ready yet.
    echo    Check logs: %COMPOSE_CMD% logs face-recognition-app
)

echo.
echo 💡 Tips:
echo    - Check container status: docker ps
echo    - View real-time logs: %COMPOSE_CMD% logs -f
echo    - Stop application: %COMPOSE_CMD% down
echo    - Open in browser: start http://localhost:5000/health

pause 