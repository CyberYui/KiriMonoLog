"""AI generation and translation helpers (free public APIs only)."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Dict, List

from kirimonolog.config import POLLINATIONS_QUERY_PARAMS, POLLINATIONS_TEXT_API


Material = Dict[str, str]
ALLOWED_AI_HOSTS = {"text.pollinations.ai", "api.mymemory.translated.net"}
MAX_TRANSLATION_LENGTH = 450


def _request_text(url: str, timeout: int = 30) -> str:
    host = urllib.parse.urlparse(url).netloc
    if host not in ALLOWED_AI_HOSTS:
        raise ValueError(f"Disallowed AI host: {host}")
    request = urllib.request.Request(url, headers={"User-Agent": "KiriMonoLog/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
        return response.read().decode("utf-8", errors="replace").strip()


def _pollinations(prompt: str) -> str:
    encoded = urllib.parse.quote(prompt, safe="")
    query = urllib.parse.urlencode(POLLINATIONS_QUERY_PARAMS)
    url = f"{POLLINATIONS_TEXT_API}/{encoded}?{query}"
    return _request_text(url)


def _strip_tail_punctuation(text: str) -> str:
    return text.rstrip("。！？.!? ")


def generate_chinese_log(materials: List[Material], date_text: str, persona_name: str, persona_profile: dict) -> str:
    bullets = "\n".join(f"- [{m['tag']}] {m['text']}（来源: {m['source']}）" for m in materials)
    prompt = (
        f"你是{persona_name}。人设：{persona_profile['identity']}"
        f"说话风格：{persona_profile['voice']}；习惯：{persona_profile['habits']}。\n"
        f"请根据以下素材写一段 150~220 字的中文日记，必须第一人称，温柔自然，不要使用emoji，不要列表。\n"
        f"日期：{date_text}\n素材：\n{bullets}"
    )

    try:
        text = _pollinations(prompt)
        if text:
            return text
    except Exception:
        pass

    first = _strip_tail_punctuation(materials[0]["text"]) if materials else "街角吹来的晚风"
    second = _strip_tail_punctuation(materials[1]["text"]) if len(materials) > 1 else "手心里慢慢安静下来的温度"
    return (
        f"今天是{date_text}。我把心情轻轻放慢，先想到「{first}」，"
        f"又被「{second}」温柔地提醒。日子并不总是发光，"
        "但我愿意把每一件小事认真收藏，像把细碎星光放进抽屉，等夜深时再慢慢看。"
    )


def translate_text(chinese_text: str, target_code: str, target_name: str) -> str:
    prompt = (
        f"Translate the following Chinese diary into natural {target_name}. "
        "Keep a gentle literary tone and preserve meaning. Return plain text only.\n"
        f"{chinese_text}"
    )

    try:
        translated = _pollinations(prompt)
        if translated:
            return translated
    except Exception:
        pass

    try:
        if len(chinese_text) > MAX_TRANSLATION_LENGTH:
            print(f"[warn] Translation input truncated to {MAX_TRANSLATION_LENGTH} chars for fallback API.")
        params = urllib.parse.urlencode({"q": chinese_text[:MAX_TRANSLATION_LENGTH], "langpair": f"zh-CN|{target_code}"})
        url = f"https://api.mymemory.translated.net/get?{params}"
        raw = _request_text(url)
        data = json.loads(raw)
        text = data.get("responseData", {}).get("translatedText", "").strip()
        if text:
            return text
    except Exception:
        pass

    return "Translation temporarily unavailable today, but the moonlight is still gentle."
