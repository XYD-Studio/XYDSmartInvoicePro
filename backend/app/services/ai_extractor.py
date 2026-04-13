import base64
import json
import requests

class InvoiceAIExtractor:
    def __init__(self, api_key: str, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    def extract_info(self, image_path: str, model_name: str) -> dict:
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"读取图片失败: {str(e)}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # >>> 核心大升级：加入内省验算逻辑，并要求输出纯数字 <<<
        system_prompt = (
            "你是一个高度严谨的财务审计大模型。请从提供的发票/票据图片中提取结构化数据。\n"
            "【极端重要规则】：\n"
            "1. 左上角通常为【发票代码】(10-12位)，右上角红色极小字体为【发票号码】(8位)。请将两者严格分开！如果只有号码，代码填'-'。\n"
            "2. 提取以下字段：['发票类型', '发票代码', '发票号码', '开票日期', '购方名称', '购方纳税人识别号', '销方名称', '销方纳税人识别号', '购买项目名称', '总金额', '税额', '价税合计']\n"
            "3. 【数学自检】：你必须自行校验 '总金额' + '税额' 是否等于 '价税合计'！如果不等，说明你看错了某些数字，请立即重新观察图片并修正！\n"
            "4. 金额数值务必输出【纯数字格式】(如 100.00)，绝对不要带有 '￥' 符号或千位逗号 ','，以方便后续数学运算。\n"
            "5. 务必以纯 JSON 格式输出，未找到的字段填 '-'。"
        )

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]
                }
            ],
            "temperature": 0.1 
        }

        url = f"{self.base_url}/chat/completions"

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", response.text)
                raise Exception(f"API 拒绝了请求: {error_msg}")

            res_json = response.json()
            content = res_json['choices'][0]['message']['content']
            
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
                
            return json.loads(content.strip())
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("AI 返回的数据不是合法的 JSON 格式")
        except KeyError:
            raise Exception("AI 返回的数据格式异常")