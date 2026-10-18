@echo off
chcp 65001 >nul
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo 净土服务已启动： http://127.0.0.1:8000
echo 关闭此窗口即停止服务。
uvicorn jingtu.api:app --host 127.0.0.1 --port 8000
pause
