@echo off
echo ==========================================
echo  MedCareerCoach Development Setup Script
echo ==========================================

echo.
echo [1/5] Checking Environment Variables...
if not exist "backend\.env" (
    echo Creating backend .env from .env.example...
    copy "backend\.env.example" "backend\.env"
) else (
    echo backend .env already exists.
)

if not exist "frontend\.env" (
    echo Creating frontend .env...
    echo VITE_API_URL=http://localhost:8000> "frontend\.env"
) else (
    echo frontend .env already exists.
)

echo.
echo [2/5] Setting up Backend Virtual Environment...
cd backend
if not exist "venv" (
    echo Creating Python venv...
    python -m venv venv
)
echo Activating venv and installing requirements...
call venv\Scripts\activate
pip install -r requirements.txt
cd ..

echo.
echo [3/5] Installing Frontend Dependencies...
cd frontend
call npm install
cd ..

echo.
echo [4/5] Installing Root Dependencies...
call npm install

echo.
echo [5/5] Setup Complete!
echo.
echo You can now start the application by running:
echo   npm run dev
echo.
echo.
