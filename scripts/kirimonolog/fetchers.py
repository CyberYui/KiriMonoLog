"""Collect daily materials from free public APIs."""

from __future__ import annotations

import json
import random
import urllib.parse
import urllib.request
from typing import Dict, List

from kirimonolog.config import FALLBACK_MATERIALS, SOURCE_ENDPOINTS


Material = Dict[str, str]
ALLOWED_SOURCE_HOSTS = {
    "v1.hitokoto.cn",
    "api.quotable.io",
    "api.adviceslip.com",
    "uselessfacts.jsph.pl",
}


def _read_json(url: str, timeout: int = 12) -> dict:
    host = urllib.parse.urlparse(url).netloc
    if host not in ALLOWED_SOURCE_HOSTS:
        raise ValueError(f"Disallowed source host: {host}")
    request = urllib.request.Request(url, headers={"User-Agent": "KiriMonoLog/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
        data = response.read().decode("utf-8", errors="replace")
    return json.loads(data)


def _from_hitokoto(payload: dict) -> Material | None:
    text = payload.get("hitokoto")
    if not text:
        return None
    source = payload.get("from") or "Hitokoto"
    return {"text": text.strip(), "source": source, "tag": "治愈文案"}


def _from_quotable(payload: dict) -> Material | None:
    text = payload.get("content")
    if not text:
        return None
    source = payload.get("author") or "Quotable"
    return {"text": text.strip(), "source": source, "tag": "生活感悟"}


def _from_advice(payload: dict) -> Material | None:
    slip = payload.get("slip") or {}
    text = slip.get("advice")
    if not text:
        return None
    return {"text": text.strip(), "source": "AdviceSlip", "tag": "情绪短句"}


def _from_fact(payload: dict) -> Material | None:
    text = payload.get("text")
    if not text:
        return None
    source = payload.get("source") or "Useless Facts"
    return {"text": text.strip(), "source": source, "tag": "趣味小知识"}


def gather_daily_materials(max_items: int = 4) -> List[Material]:
    """Fetch and normalize text materials with graceful fallback."""
    parsers = [_from_hitokoto, _from_quotable, _from_advice, _from_fact]
    items: List[Material] = []

    for endpoint, parser in zip(SOURCE_ENDPOINTS, parsers):
        try:
            payload = _read_json(endpoint)
            normalized = parser(payload)
            if normalized:
                items.append(normalized)
        except Exception:
            continue

    if not items:
        items.extend(FALLBACK_MATERIALS)

    random.shuffle(items)
    return items[:max_items]
