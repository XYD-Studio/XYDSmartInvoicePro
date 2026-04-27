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

    # >>> 检查图标文件是否存在 <<<
    icon_file = os.path.join(current_dir, "logo.ico")
    if not os.path.exists(icon_file):
        print("\n[警告] 未找到 logo.ico 文件！打包出来的程序将没有自定义图标。")
        print("建议将您的图标重命名为 logo.ico 并放置在 backend 目录下。")

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
    
    hidden_imports = [
        "fitz", 
        "requests",
        "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
        "uvicorn.protocols", "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets", "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan", "uvicorn.lifespan.on",
        "alibabacloud_ocr_api20210707", "alibabacloud_tea_openapi", "alibabacloud_tea_util"
    ]

    hidden_import_args = []
    for mod in hidden_imports:
        hidden_import_args.extend(["--hidden-import", mod])

    sep = ";" if os.name == "nt" else ":"

    args = [
        "pyinstaller",
        "--name", "SmartInvoicePro",
        "--windowed",
        "--noconsole",
        "--distpath", output_dir,
        "--add-data", f"dist{sep}dist",
        "--add-data", f"app{sep}app",
    ]
    
    # >>> 核心修改：如果存在图标，将图标文件封装进去，并替换 EXE 主图标 <<<
    if os.path.exists(icon_file):
        args.extend([
            "--icon", icon_file,                     # 替换生成的 .exe 文件图标
            "--add-data", f"logo.ico{sep}."          # 将图标打入包内供程序运行时调用
        ])

    args = args + hidden_import_args + ["desktop_main.py"]

    try:
        subprocess.run(args, check=True)
        print(f"\n✅ 打包成功！")
        print(f"可执行文件位于: {os.path.join(output_dir, 'SmartInvoicePro')}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")

if __name__ == "__main__":
    build()