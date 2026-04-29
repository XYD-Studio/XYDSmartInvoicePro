from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import shutil
import os
import uuid
import requests
import base64
from app.services.ai_extractor import InvoiceAIExtractor
from app.utils.file_parser import convert_to_image
from app.services.aliyun_ocr import AliyunOcrService

router = APIRouter()
TEMP_DIR = "./temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/process-invoice")
async def process_invoice(
    file: UploadFile = File(...),
    provider: str = Form(""),
    ai_key: str = Form(""),
    base_url: str = Form(""),
    model: str = Form(""),
    aliyun_ak: str = Form(""),
    aliyun_sk: str = Form(""),
):
    ext = file.filename.split('.')[-1].lower()
    temp_filename = f"{uuid.uuid4().hex}.{ext}"
    temp_filepath = os.path.join(TEMP_DIR, temp_filename)
    
    with open(temp_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    target_path = temp_filepath
    fallback_warning = ""

    try:
        if provider == 'aliyun-ocr':
            if not aliyun_ak or not aliyun_sk:
                raise HTTPException(status_code=400, detail="请配置完整的阿里云 AccessKey")
            try:
                ocr_service = AliyunOcrService(aliyun_ak, aliyun_sk)
                result = ocr_service.recognize(target_path)
            except Exception as ocr_err:
                if ai_key:
                    print(f"OCR识别失败 [{str(ocr_err)}]，正在自动降级调用大模型兜底...")
                    fallback_warning = f"OCR接口不可用({str(ocr_err).split(':')[0]})，已自动降级为大模型识别。"
                    if ext == 'pdf':
                        target_path = convert_to_image(temp_filepath, TEMP_DIR)
                    ai_service = InvoiceAIExtractor(api_key=ai_key, base_url=base_url)
                    result = ai_service.extract_info(target_path, model_name=model)
                else:
                    raise Exception(f"OCR解析失败且无大模型备用方案: {str(ocr_err)}")
        else:
            if not ai_key:
                raise HTTPException(status_code=400, detail="请配置大模型 API Key")
            if ext == 'pdf':
                target_path = convert_to_image(temp_filepath, TEMP_DIR)
            ai_service = InvoiceAIExtractor(api_key=ai_key, base_url=base_url)
            result = ai_service.extract_info(target_path, model_name=model)
            
        return {"status": "success", "data": result, "fallback_warning": fallback_warning}
        
    except Exception as e:
        print(f"\n[Error processing {file.filename}]: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(temp_filepath):
            try: os.remove(temp_filepath)
            except: pass
        if target_path and target_path != temp_filepath and os.path.exists(target_path):
            try: os.remove(target_path)
            except: pass


@router.post("/test-api")
async def test_api(
    provider: str = Form(...),
    api_key: str = Form(""),
    base_url: str = Form(""),
    model: str = Form(""),
    aliyun_ak: str = Form(""),
    aliyun_sk: str = Form("")
):
    if provider == 'aliyun-ocr':
        try:
            from alibabacloud_ocr_api20210707.client import Client as OcrApiClient
            from alibabacloud_tea_openapi import models as open_api_models
            from alibabacloud_tea_util import models as util_models
            import alibabacloud_ocr_api20210707.models as ocr_api_models
            
            config = open_api_models.Config(access_key_id=aliyun_ak, access_key_secret=aliyun_sk, endpoint='ocr-api.cn-hangzhou.aliyuncs.com')
            client = OcrApiClient(config)
            try:
                req = ocr_api_models.RecognizeVatInvoiceRequest() if hasattr(ocr_api_models, 'RecognizeVatInvoiceRequest') else ocr_api_models.RecognizeAdvancedRequest()
                client.recognize_vat_invoice_with_options(req, util_models.RuntimeOptions())
            except Exception as e:
                err_msg = str(e)
                if "InvalidAccessKeyId" in err_msg or "SignatureDoesNotMatch" in err_msg:
                    return {"status": "error", "message": "AK/SK 不合法，请检查！"}
            return {"status": "success", "message": "OCR 引擎连接成功，AK/SK 合法！"}
        except Exception as e:
            return {"status": "error", "message": f"连接失败: {str(e)}"}
    else:
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        payload = {"model": model, "messages": [{"role": "user", "content": "hello"}], "max_tokens": 10}
        try:
            url = f"{base_url.rstrip('/')}/chat/completions"
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                return {"status": "success", "message": "API 连接成功！"}
            else:
                return {"status": "error", "message": f"鉴权或模型错误: {response.text}"}
        except Exception as e:
             return {"status": "error", "message": f"网络拒绝连接: {str(e)}"}


# >>> 新增：专为桌面端设计的“系统原生另存为”接口 <<<
class SaveExcelRequest(BaseModel):
    filename: str
    b64_data: str

@router.post("/save-excel")
async def save_excel(req: SaveExcelRequest):
    try:
        import webview
        # 如果没有打开任何桌面窗口 (例如在纯网页模式运行)，则拒绝
        if not webview.windows:
            return {"status": "error", "message": "非桌面环境，无法调用原生对话框"}
        
        # 获取当前的桌面主窗口
        window = webview.windows[0]
        
        # 唤起 Windows 系统的原生“另存为”对话框
        result = window.create_file_dialog(
            webview.SAVE_DIALOG, 
            directory='', 
            save_filename=req.filename, 
            file_types=('Excel 工作表 (*.xlsx)', '所有文件 (*.*)')
        )
        
        if result and len(result) > 0:
            save_path = result[0]
            # 把前端传过来的 Base64 Excel 数据解码并写入到用户选择的路径
            with open(save_path, "wb") as f:
                f.write(base64.b64decode(req.b64_data))
            return {"status": "success", "message": "保存成功！", "path": save_path}
        else:
            return {"status": "cancelled", "message": "用户取消保存"}
    except Exception as e:
        return {"status": "error", "message": str(e)}