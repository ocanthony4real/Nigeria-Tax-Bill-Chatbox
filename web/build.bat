@echo off
REM Build script for Windows

echo Building frontend...
cd frontend
call npm install
call npm run build

echo Copying static files...
if not exist "..\static" mkdir ..\static
xcopy /E /Y out\* ..\static\

echo Done! Run with: uvicorn main:app --reload
cd ..
