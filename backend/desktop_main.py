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
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="critical")

if __name__ == '__main__':
    dist_path = get_resource_path("dist")
    if os.path.exists(dist_path):
        app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")

    # 获取图标的绝对路径
    icon_path = get_resource_path("logo.ico")

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    time.sleep(1)
    
    # 在这里添加 icon_path 参数！
    window = webview.create_window(
        'SmartInvoice 智能票据助手', 
        'http://127.0.0.1:8000', 
        width=1366, 
        height=850,
        min_size=(1024, 768)
    )
    
    # 强制在 Windows 平台下将窗口图标设置为我们自定义的 ico
    webview.start(debug=False, gui='edge', icon=icon_path)