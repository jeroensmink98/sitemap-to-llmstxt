@echo off
REM 🚀 Sitemap to LLMS.txt Deployment Script (Windows)
REM This script automates the deployment process for Windows users

echo 🚀 Starting deployment of Sitemap to LLMS.txt...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed. Please install it first.
    pause
    exit /b 1
)

REM Navigate to docker directory
if not exist "docker\docker-compose.prod.yml" (
    echo [ERROR] Production Docker Compose file not found. Please run this script from the project root.
    pause
    exit /b 1
)

cd docker

REM Check if we need to update the API_BASE_URL
findstr "your-domain.com" docker-compose.prod.yml >nul
if %errorlevel% equ 0 (
    echo [WARNING] Please update the API_BASE_URL in docker-compose.prod.yml with your actual domain before continuing.
    echo Current configuration:
    findstr /A "API_BASE_URL" docker-compose.prod.yml
    echo.
    set /p "continue=Have you updated the domain? (y/N): "
    if /i not "%continue%"=="y" (
        echo [ERROR] Please update the domain configuration first.
        pause
        exit /b 1
    )
)

REM Stop existing containers if running
echo [INFO] Stopping existing containers...
docker-compose -f docker-compose.prod.yml down 2>nul

REM Remove old images to ensure fresh build
echo [INFO] Removing old images...
docker-compose -f docker-compose.prod.yml down --rmi all 2>nul

REM Build and start services
echo [INFO] Building and starting services...
docker-compose -f docker-compose.prod.yml up -d --build

REM Wait for services to be healthy
echo [INFO] Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

REM Check service status
echo [INFO] Checking service status...
docker-compose -f docker-compose.prod.yml ps

echo.
echo 🚀 Deployment completed!
echo.
echo 📋 Service Status:
echo    Frontend: http://localhost (or your domain)
echo    Backend API: http://localhost:8000
echo    Health Check: http://localhost/api/health
echo.
echo 🔧 Useful Commands:
echo    View logs: docker-compose -f docker-compose.prod.yml logs -f
echo    Stop services: docker-compose -f docker-compose.prod.yml down
echo    Restart services: docker-compose -f docker-compose.prod.yml restart
echo    View status: docker-compose -f docker-compose.prod.yml ps
echo.
echo 📚 For more information, see DEPLOYMENT.md
echo.
pause
