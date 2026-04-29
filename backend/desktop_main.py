import uvicorn
import threading
import webview
import os
import sys
import time
from fastapi.staticfiles import StaticFiles
from app.main import app

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def start_server():
    # >>> 端口改为 8888 <<<
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="critical")

def on_closed():
    print("窗口已关闭，正在强制释放资源...")
    os._exit(0)

if __name__ == '__main__':
    dist_path = get_resource_path("dist")
    if os.path.exists(dist_path):
        app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")

    icon_path = get_resource_path("logo.ico")

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    time.sleep(1)
    
    window = webview.create_window(
        'SmartInvoice 智能票据助手', 
        'http://127.0.0.1:8888', # >>> 访问地址改为 8888 <<<
        width=1366, 
        height=850,
        min_size=(1024, 768)
    )
    
    window.events.closed += on_closed

    webview.start(
        debug=False, 
        gui='edge', 
        icon=icon_path, 
        private_mode=False
    )