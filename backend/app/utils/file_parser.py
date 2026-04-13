import os
import fitz  # PyMuPDF

def convert_to_image(file_path: str, output_dir: str) -> str:
    """
    将 PDF 转换为高清图片，并确保安全释放文件句柄
    """
    ext = file_path.lower().split('.')[-1]
    filename = os.path.basename(file_path).split('.')[0]
    out_path = os.path.join(output_dir, f"{filename}.jpg")

    if ext in ['jpg', 'jpeg', 'png']:
        return file_path
    
    elif ext == 'pdf':
        doc = None
        try:
            doc = fitz.open(file_path)
            page = doc.load_page(0) # 发票通常只有一页，取第一页
            # 矩阵放大 2 倍，提高清晰度，防止 AI 认错小字
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            pix.save(out_path)
            return out_path
        except Exception as e:
            raise Exception(f"PDF 转换图片失败: {str(e)}")
        finally:
            # 【修复 500 报错的关键】：必须显式关闭！否则 Windows 下无法删除临时文件会直接引发崩溃
            if doc is not None:
                doc.close()
    else:
        raise ValueError(f"不支持的文件格式: {ext}")