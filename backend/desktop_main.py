import uvicorn
import threading
import webview
import os
import sys
import time
from fastapi.staticfiles import StaticFiles
from app.main import app

def get_resource_path(relative_path):
    """动态获取打包后资源解压的临时绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def start_server():
    """在子线程中启动 FastAPI 服务器"""
    # 生产环境中关掉 reload，提升稳定性
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="critical")

def on_closed():
    """【核心修复】：监听窗口关闭事件，瞬间强杀整个进程树，释放 8000 端口和缓存锁"""
    print("窗口已关闭，正在强制释放资源...")
    os._exit(0)

if __name__ == '__main__':
    # 1. 挂载前端静态文件
    dist_path = get_resource_path("dist")
    if os.path.exists(dist_path):
        app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")

    # 2. 获取图标
    icon_path = get_resource_path("logo.ico")

    # 3. 开启后端服务
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    # 稍微等一秒，确保 8000 端口被成功绑定
    time.sleep(1)
    
    # 4. 创建桌面窗口
    window = webview.create_window(
        'SmartInvoice 智能票据助手', 
        'http://127.0.0.1:8888', 
        width=1366, 
        height=850,
        min_size=(1024, 768)
    )
    
    # >>> 绑定窗口关闭事件 <<<
    window.events.closed += on_closed

    # 5. 启动内核
    webview.start(
        debug=False, 
        gui='edge', 
        icon=icon_path, 
        private_mode=False
    )