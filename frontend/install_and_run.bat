@echo off
set PATH=%PATH%;C:\Program Files\nodejs
cd /d C:\Users\ryuya\Downloads\job-support-app\frontend
echo Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    exit /b %errorlevel%
)
echo Starting development server...
call npm run dev
