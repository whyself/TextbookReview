import os
import requests
import json
import base64
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

# 从环境变量获取 TextIn 配置
APP_ID = os.getenv("TEXTIN_APP_ID")
SECRET_CODE = os.getenv("TEXTIN_SECRET_CODE")

@tool
def extract_field(file_path: str, fields: list[str] = None) -> str:
    """
    使用 TextIn XParse 智能抽取 API (Schema Mode)，主要用于结构化的【申报书/表格】。
    
    Args:
        file_path: 文件的绝对路径。
        fields: 需要提取的字段列表，例如 ["教材名称", "作者", "ISBN"]。
    
    Returns:
        JSON 格式的提取结果字符串。
    """
    print(f"\n[TextIn:Extract] 正在处理文件: {file_path}\n{fields}\n", flush=True)
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."

    if not fields:
        return "Error: No fields provided."

    # 1. 读取文件并转换为 Base64
    try:
        with open(file_path, 'rb') as fp:
            file_content = fp.read()
            file_base64 = base64.b64encode(file_content).decode('utf-8')
    except Exception as e:
        return f"Error reading file: {str(e)}"

    # 2. 构造 Schema
    properties = {}
    for field in fields:
        properties[field] = {
            "type": ["string", "null"],
            "description": field
        }

    schema = {
        "type": "object",
        "properties": properties,
    }

    # 3. 构造请求 Payload
    url = "https://api.textin.com/ai/service/v3/entity_extraction"
    
    payload = {
        "file": {
            "file_base64": file_base64,
            "file_name": os.path.basename(file_path)
        },
        "schema": schema,
        "parse_options": {
            "crop_dewarp": 1,
            "get_image": "none"
        },
        "extract_options": {
            "generate_citations": False,
            "stamp": False
        }
    }

    headers = {
        "x-ti-app-id": APP_ID,
        "x-ti-secret-code": SECRET_CODE,
        "Content-Type": "application/json"
    }

    # 4. 发送请求
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        # 检查 HTTP 状态码
        if response.status_code != 200:
            return f"Error: TextIn API returned status code {response.status_code}. Response: {response.text}"
        
        result_json = response.json()
        
        # 5. 解析并返回结果
        # TextIn 成功时的 error_code 通常为 0
        if result_json.get("code") == 200:
            extracted_data = result_json.get("result", {})
            print(f"{file_path} [TextIn:Extract] 提取结果: Success", flush=True)
            return json.dumps(extracted_data, ensure_ascii=False, indent=2)
        else:
            msg = result_json.get('message', 'Unknown error')
            code = result_json.get('error_code') or result_json.get('code')
            print(f"Error from TextIn Extract API: {msg} (Code: {code})", flush=True)
            return f"Error from TextIn API: {msg} (Code: {code})"

    except Exception as e:
        return f"Exception during TextIn API call: {str(e)}"


@tool
def parse_text(file_path: str) -> str:
    """
    使用 TextIn XParse 通用文档解析 API (Markdown Mode)，用于处理【附件、非结构化文档、结构奇怪的材料】。
    
    Args:
        file_path: 文件的绝对路径（支持 PDF, JPG, DOC, DOCX 等）。
    
    Returns:
        解析后的 Markdown 格式全文内容。
    """
    print(f"\n[TextIn:Parse] 正在解析全文: {file_path}", flush=True)
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."

    # 1. 构造请求 URL (通用文档解析 API)
    # 根据文档: https://api.textin.com/ai/service/v3/recognize
    # 注意：URL参数可以直接拼在 URL 后，也可以作为 binary body 发送
    # 这里我们使用 Python SDK 风格的 raw binary 请求
    
    # 文档转 Markdown 标准接口
    base_url = "https://api.textin.com/ai/service/v1/pdf_to_markdown"
    
    # 构造参数
    params = {
        "markdown_details": 1,
        "page_count": 50, # 限制解析页数，避免太长
        "parse_mode": "auto",
        "table_flavor": "markdown" # 使用 md 格式输出表格，Agent 更容易读
    }

    headers = {
        "x-ti-app-id": APP_ID,
        "x-ti-secret-code": SECRET_CODE,
        # 注意：这里我们直接发送二进制流，不是 JSON
        "Content-Type": "application/octet-stream" 
    }

    # 2. 发送请求
    try:
        with open(file_path, 'rb') as fp:
            file_content = fp.read()
        
        # requests 自动处理 params 的 URL 编码
        response = requests.post(base_url, params=params, headers=headers, data=file_content)
        
        result_json = response.json()
        
        # 3. 解析结果
        # 通用文档解析 API 的返回结构：result -> markdown
        is_success = (
            result_json.get("code") == 200 or 
            result_json.get("error_code") == 0 or
            ("result" in result_json and "markdown" in result_json.get("result", {}))
        )

        if is_success:
            markdown_content = result_json.get("result", {}).get("markdown", "")
            print(f"{file_path} [TextIn:Parse] 解析成功 (长度: {len(markdown_content)})", flush=True)
            # 截断一下避免爆 Agent 上下文，或者直接返回
            return markdown_content
        else:
            msg = result_json.get('message', 'Unknown error')
            code = result_json.get('error_code') or result_json.get('code')
            print(f"Error from TextIn Parse API: {msg} (Code: {code})", flush=True)
            return f"Error from TextIn Parse API: {msg} (Code: {code})"

    except Exception as e:
        return f"Exception during TextIn Parse API call: {str(e)}"
