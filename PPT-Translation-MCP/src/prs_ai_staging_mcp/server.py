import mimetypes
import os
import re
from typing import Optional
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field


mcp = FastMCP("PrsAi Staging MCP Server", log_level="INFO")


def normalize_str(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if (text.startswith("`") and text.endswith("`")) or (
        text.startswith("\"") and text.endswith("\"")
    ):
        text = text[1:-1].strip()
    return text


def read_dotenv_value(key: str) -> str:
    dotenv_path = Path(__file__).resolve().parents[3] / ".env"
    if not dotenv_path.exists():
        return ""

    try:
        content = dotenv_path.read_text(encoding="utf-8")
    except Exception:
        return ""

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() != key:
            continue
        return normalize_str(v)
    return ""


def get_base_url() -> str:
    return os.getenv("PRS_AI_MCP_BASE_URL", "https://prsai.cc").rstrip("/")


def resolve_api_key(api_key: Optional[str]) -> str:
    if api_key and api_key.strip():
        return api_key.strip()
    env_key = os.getenv("PRS_AI_MCP_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    dotenv_key = read_dotenv_value("PRS_AI_MCP_API_KEY")
    if dotenv_key:
        return dotenv_key
    raise ValueError("缺少 api_key：请传入参数 api_key 或设置环境变量 PRS_AI_MCP_API_KEY")


def resolve_ppt_id(ppt_id: str) -> str:
    normalized = normalize_str(ppt_id)
    if not normalized:
        raise ValueError("ppt_id 不能为空")
    return normalized


def raise_for_api_status(resp: httpx.Response) -> None:
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise Exception(
            f"API请求失败: HTTP {e.response.status_code} - {e.response.text}"
        ) from e


@mcp.tool()
async def upload_file(
    file_path: str = Field(description="需要上传的文件本地绝对路径"),
    api_key: Optional[str] = Field(
        default=None,
        description="接口 mcpToken（作为 api_key 使用）。不传则读取 PRS_AI_MCP_API_KEY",
    ),
) -> dict:
    file_path = file_path.strip().replace("\\ ", " ").replace("\\&", "&")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    token = resolve_api_key(api_key)
    base_url = get_base_url()
    url = f"{base_url}/api/mcp/file/upload"

    filename = os.path.basename(file_path)
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"

    timeout = httpx.Timeout(300.0, connect=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        with open(file_path, "rb") as f:
            files = {"file": (filename, f, content_type)}
            data = {"mcpToken": token}
            resp = await client.post(url, files=files, data=data)
            raise_for_api_status(resp)
            res = resp.json()
            if isinstance(res, dict):
                uploaded_url = normalize_str(res.get("data"))
                if uploaded_url:
                    res["uploaded_url"] = uploaded_url
                    res["ppt_url"] = uploaded_url
                    res["pptUrl"] = uploaded_url
            return res


@mcp.tool()
async def translate_ppt(
    ppt_url: str = Field(description="需要翻译的PPT文件URL地址"),
    file_original_name: str = Field(description="原文件名（带 .ppt/.pptx 后缀）"),
    translate_language: str = Field(default="en", description="目标语言代码，如 en"),
    api_key: Optional[str] = Field(
        default=None,
        description="接口 mcpToken（作为 api_key 使用）。不传则读取 PRS_AI_MCP_API_KEY",
    ),
) -> dict:
    token = resolve_api_key(api_key)
    ppt_url = normalize_str(ppt_url)
    file_original_name = normalize_str(file_original_name)
    translate_language = normalize_str(translate_language) or "en"

    if not ppt_url:
        raise ValueError("ppt_url 不能为空")
    if not file_original_name:
        raise ValueError("file_original_name 不能为空")

    base_url = get_base_url()
    url = f"{base_url}/api/mcp/ppt/task/add"

    payload = {
        "translateLanguage": translate_language,
        "pptUrl": ppt_url,
        "mcpToken": token,
        "fileOriginalName": file_original_name,
    }

    timeout = httpx.Timeout(120.0, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload)
        raise_for_api_status(resp)
        res = resp.json()

        data = res.get("data") if isinstance(res, dict) else None
        if isinstance(res, dict):
            task_id = normalize_str(data)
            if task_id:
                res["task_id"] = task_id
                res["outppt_url"] = f"{base_url}/#/progress/{task_id}"
            else:
                res["outppt_url"] = ""
        return res


@mcp.tool()
async def get_ppt_task_status(
    ppt_id: str = Field(description="PPT翻译任务 ID"),
    api_key: Optional[str] = Field(
        default=None,
        description="接口 mcpToken（作为 api_key 使用）。不传则读取 PRS_AI_MCP_API_KEY",
    ),
) -> dict:
    """查询 PPT 翻译任务状态，仅返回 pptId、status 和 translateLanguage。

    翻译耗时较长。创建翻译任务后应先等待至少 60 秒再首次调用本工具；
    当 status 为 0（待处理）或 1（处理中）时，应等待至少 60 秒后再次查询，
    不要频繁轮询。status 为 2 表示已完成，3 表示已失败。
    """
    token = resolve_api_key(api_key)
    ppt_id = resolve_ppt_id(ppt_id)
    url = f"{get_base_url()}/api/mcp/ppt/task/plan"

    timeout = httpx.Timeout(60.0, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url, params={"pptId": ppt_id, "mcpToken": token})
        raise_for_api_status(resp)
        res = resp.json()

    if not isinstance(res, dict):
        raise ValueError("API返回格式错误：期望 JSON 对象")
    data = res.get("data")
    source = data if isinstance(data, dict) else res
    status = source.get("status")
    translate_language = source.get("translateLanguage")
    if status is None:
        raise ValueError(f"API返回缺少 status 字段: {res}")
    return {
        "pptId": normalize_str(source.get("pptId")) or ppt_id,
        "status": status,
        "translateLanguage": translate_language,
    }


@mcp.tool()
async def download_ppt(
    ppt_id: str = Field(description="PPT翻译任务 ID"),
    output_path: Optional[str] = Field(
        default=None,
        description="下载文件保存路径。不传时保存为当前目录下的 <ppt_id>.pptx",
    ),
    api_key: Optional[str] = Field(
        default=None,
        description="接口 mcpToken（作为 api_key 使用）。不传则读取 PRS_AI_MCP_API_KEY",
    ),
) -> dict:
    """下载已完成的 PPT 翻译结果到本地。"""
    token = resolve_api_key(api_key)
    ppt_id = resolve_ppt_id(ppt_id)
    url = f"{get_base_url()}/api/mcp/ppt/task/download"

    timeout = httpx.Timeout(300.0, connect=60.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        resp = await client.get(url, params={"pptId": ppt_id, "mcpToken": token})
        raise_for_api_status(resp)

    content_type = resp.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        raise ValueError(f"下载接口未返回 PPT 文件: {resp.json()}")

    if output_path:
        destination = Path(output_path.strip()).expanduser()
        if destination.exists() and destination.is_dir():
            destination = destination / f"{ppt_id}.pptx"
    else:
        destination = Path.cwd() / f"{ppt_id}.pptx"

    content_disposition = resp.headers.get("content-disposition", "")
    filename_match = re.search(r'filename="?([^";]+)', content_disposition)
    if not output_path and filename_match:
        response_filename = Path(filename_match.group(1)).name
        if response_filename:
            destination = Path.cwd() / response_filename

    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(resp.content)
    return {
        "file_path": str(destination),
        "file_size": len(resp.content),
    }
