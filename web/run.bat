@echo off
cd /d "C:\Users\ocant\Documents\Nigeria Tax Bill Chatbot\web"
"C:\Users\ocant\Documents\Nigeria Tax Bill Chatbot\.venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000
