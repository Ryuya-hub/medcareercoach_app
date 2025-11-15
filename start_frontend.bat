@echo off
set PATH=%PATH%;C:\Program Files\nodejs
cd /d "C:\Users\ryuya\Downloads\job-support-app\frontend"
echo Starting frontend development server on port 3000...
call npm run dev
