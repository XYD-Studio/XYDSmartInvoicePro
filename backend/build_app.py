import os
import shutil
import subprocess
import sys

def build():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    os.chdir(current_dir)
    print(f"当前工作目录: {current_dir}")

    dist_dir = os.path.join(current_dir, "dist")
    if not os.path.exists(dist_dir) or not os.listdir(dist_dir):
        print("\n[错误] 未找到前端静态文件！")
        sys.exit(1)

    icon_file = os.path.join(current_dir, "logo.ico")
    if not os.path.exists(icon_file):
        print("\n[警告] 未找到 logo.ico 文件！")

    build_dir = os.path.join(current_dir, "build")
    spec_file = os.path.join(current_dir, "SmartInvoicePro.spec")
    output_dir = os.path.join(current_dir, "dist_app")

    for folder in [build_dir, output_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"已清理旧文件夹: {folder}")
            
    if os.path.exists(spec_file):
        os.remove(spec_file)

    print("\n开始执行 PyInstaller 编译 (这可能需要几分钟)...\n")
    
    # 隐式依赖
    hidden_imports = [
        "fitz", 
        "requests",
        "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
        "uvicorn.protocols", "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets", "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan", "uvicorn.lifespan.on",
        "alibabacloud_ocr_api20210707", "alibabacloud_tea_openapi", "alibabacloud_tea_util"
    ]

    # 黑名单瘦身
    excludes = [
        "tkinter", "unittest", "matplotlib", "numpy", "pandas", 
        "PyQt5", "PyQt6", "PySide2", "PySide6", "scipy", "notebook",
        "IPython", "pydoc"
    ]

    sep = ";" if os.name == "nt" else ":"

    # 1. 基础参数
    args = [
        "pyinstaller",
        "--name", "SmartInvoicePro",
        "--windowed",
        "--noconsole",
        "--distpath", output_dir,
        "--add-data", f"dist{sep}dist",
        "--add-data", f"app{sep}app"
    ]

    # 2. 追加图标参数
    if os.path.exists(icon_file):
        args.extend([
            "--icon", icon_file,
            "--add-data", f"logo.ico{sep}."
        ])

    # 3. 追加隐式依赖参数
    for mod in hidden_imports:
        args.extend(["--hidden-import", mod])

    # 4. 追加黑名单参数
    for mod in excludes:
        args.extend(["--exclude-module", mod])

    # 5. 最后必须且只能追加一次主程序脚本！
    args.append("desktop_main.py")

    try:
        # check=True 会在命令失败时抛出异常
        subprocess.run(args, check=True)
        print(f"\n✅ 打包成功！")
        print(f"可执行文件位于: {os.path.join(output_dir, 'SmartInvoicePro')}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败，错误码: {e.returncode}")

if __name__ == "__main__":
    build()