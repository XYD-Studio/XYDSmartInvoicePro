import json
from alibabacloud_ocr_api20210707.client import Client as OcrApiClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_api_models
from alibabacloud_tea_util import models as util_models

class AliyunOcrService:
    def __init__(self, access_key_id: str, access_key_secret: str):
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint='ocr-api.cn-hangzhou.aliyuncs.com'
        )
        self.client = OcrApiClient(config)

    def recognize(self, file_path: str) -> dict:
        try:
            with open(file_path, 'rb') as f:
                request = ocr_api_models.RecognizeVatInvoiceRequest(body=f)
                runtime = util_models.RuntimeOptions()
                # 专门调用增值税发票接口（天然支持 PDF、OFD、JPG）
                response = self.client.recognize_vat_invoice_with_options(request, runtime)
                
                res_dict = json.loads(response.body.data)
                content = res_dict.get('content', {})
                
                # 将 OCR 字段映射为我们台账的标准字段
                return {
                    "发票类型": content.get("invoiceType", "发票"),
                    "发票代码": content.get("invoiceCode", "-"),
                    "发票号码": content.get("invoiceNo", "-"),
                    "开票日期": content.get("invoiceDate", "-"),
                    "购方名称": content.get("purchaserName", "-"),
                    "购方纳税人识别号": content.get("purchaserTaxNo", "-"),
                    "销方名称": content.get("payeeName", "-"),
                    "销方纳税人识别号": content.get("payeeTaxNo", "-"),
                    "购买项目名称": content.get("itemName", "-"), # OCR自带商品明细汇总
                    "税额": content.get("taxAmount", "-"),
                    "总金额": content.get("withoutTaxAmount", "-"),
                    "价税合计": content.get("invoiceAmount", "-")
                }
        except Exception as e:
            raise Exception(f"阿里云OCR解析失败，请检查 AK/SK 或额度: {str(e)}")