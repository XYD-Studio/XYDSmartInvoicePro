@echo off
chcp 65001 >nul
title SmartInvoice Pro 商业版控制台
echo ========================================
echo   SmartInvoice Pro 正在启动...
echo ========================================

:: 启动后端 (新开一个最小化的窗口运行)
echo 正在启动后端服务 (FastAPI)...
start /min cmd /c "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

:: 启动前端
echo 正在启动前端服务 (Vue3 + Vite)...
cd frontend
npm run dev

pause