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
            "你是一个高度严谨的中国税务发票审计 AI。请从提供的发票/票据图片中精准提取结构化数据。\n"
            "【极端重要规则】：\n"
            "1. 【发票号码】提取规则：如果是传统纸质发票，请提取右上角的8位号码；如果是最新版'全面数字化的电子发票'(全电发票)，其右上角只有一排黑色的20位数字，这就是【发票号码】。如果票面明确区分了发票代码和发票号码，请将它们用横线拼接(如'123-456')填入【发票号码】中。\n"
            "2. 提取以下字段：['发票类型', '发票号码', '开票日期', '购方名称', '购方纳税人识别号', '销方名称', '销方纳税人识别号', '购买项目名称', '总金额', '税额', '价税合计']\n"
            "3. 【数学逻辑自检】：你必须在内部验算 '总金额' + '税额' 是否严格等于 '价税合计'！如果不等，说明你看错了某些数字，请立即重新观察图片并修正！\n"
            "4. 所有金额数值务必输出【纯数字格式】(如 100.00)，绝对不要带有 '￥' 符号或千位逗号 ','。\n"
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