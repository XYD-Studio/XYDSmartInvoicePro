from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil
import os
import uuid
import requests
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
    fallback_warning = "" # 用于记录降级警告

    try:
        # 分支 1：增值税专用 OCR 引擎
        if provider == 'aliyun-ocr':
            if not aliyun_ak or not aliyun_sk:
                raise HTTPException(status_code=400, detail="请配置完整的阿里云 AccessKey")
            
            try:
                # 尝试使用 OCR
                ocr_service = AliyunOcrService(aliyun_ak, aliyun_sk)
                result = ocr_service.recognize(target_path)
            except Exception as ocr_err:
                # 【核心商业逻辑：自动降级机制】
                # 如果 OCR 失败，但用户同时配置了大模型 (ai_key)，则自动无缝降级到大模型去识别
                if ai_key:
                    print(f"OCR识别失败 [{str(ocr_err)}]，正在自动降级调用大模型兜底...")
                    fallback_warning = f"OCR接口不可用({str(ocr_err).split(':')[0]})，已自动降级为大模型识别。"
                    
                    if ext == 'pdf':
                        target_path = convert_to_image(temp_filepath, TEMP_DIR)
                    ai_service = InvoiceAIExtractor(api_key=ai_key, base_url=base_url)
                    result = ai_service.extract_info(target_path, model_name=model)
                else:
                    # 如果用户连备用的大模型也没配，那就只能报错了
                    raise Exception(f"OCR解析失败且无大模型备用方案: {str(ocr_err)}")
            
        # 分支 2：直接选用视觉大模型引擎
        else:
            if not ai_key:
                raise HTTPException(status_code=400, detail="请配置大模型 API Key")
            if ext == 'pdf':
                target_path = convert_to_image(temp_filepath, TEMP_DIR)
            ai_service = InvoiceAIExtractor(api_key=ai_key, base_url=base_url)
            result = ai_service.extract_info(target_path, model_name=model)
            
        # 将可能的降级警告一并返回给前端
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
                # 兼容不同版本 SDK 的类名
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