"""每日素材抓取模块。

本模块负责从四个免费公开 API 抓取文本素材，并将其统一转换为 Material 格式。
每个 API 有对应的解析器函数，负责从原始 JSON 中提取所需字段。

安全机制：
- 使用 ALLOWED_SOURCE_HOSTS 白名单限制允许请求的域名，防止 SSRF 攻击
- 请求超时设为 12 秒，避免单个端点阻塞整体流程
- 任何端点失败都会自动跳过，最终回退到 FALLBACK_MATERIALS

数据流：
  SOURCE_ENDPOINTS → _read_json() → 解析器 → Material dict → gather_daily_materials()
"""

from __future__ import annotations

import json
import random
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List

from kirimonolog.config import FALLBACK_MATERIALS, SOURCE_ENDPOINTS

# Material 类型别名：每条素材是一个包含 text/source/tag 三个键的字典
Material = Dict[str, str]

# 允许请求的素材源域名白名单（安全机制，防止 SSRF）
ALLOWED_SOURCE_HOSTS = {
    "v1.hitokoto.cn",
    "api.quotable.io",
    "api.adviceslip.com",
    "uselessfacts.jsph.pl",
}


def _read_json(url: str, timeout: int = 12) -> dict:
    """发起 HTTP GET 请求并解析 JSON 响应。

    Args:
        url     : 目标 URL（必须在 ALLOWED_SOURCE_HOSTS 白名单中）
        timeout : 请求超时时间（秒），默认 12 秒

    Returns:
        解析后的 JSON 字典

    Raises:
        ValueError        : URL 域名不在白名单中
        urllib.error.URLError : 网络请求失败
        json.JSONDecodeError  : 响应不是合法 JSON
    """
    host = urllib.parse.urlparse(url).netloc
    if host not in ALLOWED_SOURCE_HOSTS:
        raise ValueError(f"Disallowed source host: {host}")
    request = urllib.request.Request(url, headers={"User-Agent": "KiriMonoLog/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
        data = response.read().decode("utf-8", errors="replace")
    return json.loads(data)


# ── 各 API 的解析器函数 ──
# 每个解析器接收原始 JSON dict，返回标准化的 Material dict 或 None（解析失败时）

def _from_hitokoto(payload: dict) -> Material | None:
    """解析一言（Hitokoto）API 的响应。

    返回格式示例：
        {"hitokoto": "句子内容", "from": "出处"}
    tag 固定为"治愈文案"。
    """
    text = payload.get("hitokoto")
    if not text:
        return None
    source = payload.get("from") or "Hitokoto"
    return {"text": text.strip(), "source": source, "tag": "治愈文案"}


def _from_quotable(payload: dict) -> Material | None:
    """解析 Quotable API 的响应。

    返回格式示例：
        {"content": "Quote text", "author": "Author Name"}
    tag 固定为"生活感悟"。
    """
    text = payload.get("content")
    if not text:
        return None
    source = payload.get("author") or "Quotable"
    return {"text": text.strip(), "source": source, "tag": "生活感悟"}


def _from_advice(payload: dict) -> Material | None:
    """解析 AdviceSlip API 的响应。

    返回格式示例：
        {"slip": {"advice": "Advice text"}}
    tag 固定为"情绪短句"。
    """
    slip = payload.get("slip") or {}
    text = slip.get("advice")
    if not text:
        return None
    return {"text": text.strip(), "source": "AdviceSlip", "tag": "情绪短句"}


def _from_fact(payload: dict) -> Material | None:
    """解析 Useless Facts API 的响应。

    返回格式示例：
        {"text": "Fact text", "source": "source name"}
    tag 固定为"趣味小知识"。
    """
    text = payload.get("text")
    if not text:
        return None
    source = payload.get("source") or "Useless Facts"
    return {"text": text.strip(), "source": source, "tag": "趣味小知识"}


def gather_daily_materials(max_items: int = 4) -> List[Material]:
    """抓取并汇总当日素材，带有优雅降级（graceful fallback）机制。

    工作流程：
    1. 按顺序遍历 SOURCE_ENDPOINTS，对每个端点调用对应的解析器
    2. 如果某个端点失败（超时/网络错误/解析错误），自动跳过继续下一个
    3. 如果所有端点都失败，使用 FALLBACK_MATERIALS 作为备用素材
    4. 随机打乱素材顺序，取前 max_items 条返回

    Args:
        max_items : 返回的最大素材条数，默认 4 条

    Returns:
        Material 字典列表，每个字典包含 text/source/tag 三个键
    """
    # 解析器列表与 SOURCE_ENDPOINTS 一一对应
    parsers = [_from_hitokoto, _from_quotable, _from_advice, _from_fact]
    items: List[Material] = []

    for endpoint, parser in zip(SOURCE_ENDPOINTS, parsers):
        try:
            payload = _read_json(endpoint)
            normalized = parser(payload)
            if normalized:
                items.append(normalized)
        except (json.JSONDecodeError, urllib.error.URLError, TimeoutError, ValueError):
            # 任何异常都跳过当前端点，不影响其他端点的抓取
            continue

    # 如果所有外部 API 都没有返回有效素材，使用内置备用素材
    if not items:
        items.extend(FALLBACK_MATERIALS)

    # 随机打乱后截取，保证每次生成的日志素材组合不同
    random.shuffle(items)
    return items[:max_items]
