"""AI generation and translation helpers (free public APIs only)."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List

from kirimonolog.config import POLLINATIONS_QUERY_PARAMS, POLLINATIONS_TEXT_API


Material = Dict[str, str]
ALLOWED_AI_HOSTS = {"text.pollinations.ai", "api.mymemory.translated.net"}
MAX_TRANSLATION_LENGTH = 450
LOGGER = logging.getLogger(__name__)

# ── 本地 fallback 日记模板（按日期选择，确保每天不同） ──
FALLBACK_DIARY_TEMPLATES = [
    # 温暖日常型
    lambda d, mats, nm: (
        f"今天是{d}，一个{['普普通通却让人安心的日子', '淡淡阳光洒进窗台的日子', '风很轻很轻的日子'][int(d[-1])%3]}。"
        f"{nm}翻着今天收集的小碎片，「{mats[0]['text']}」——这是我今天最想记住的一句话。"
        f"{['有时候最好的治愈，就是允许自己什么都不做。', '慢慢来，日子会自己排好队的。', '安静地度过一天，也是一种了不起的事。'][(int(d[-1])+1)%3]}"
    ),
    # 浪漫细腻型
    lambda d, mats, nm: (
        f"{d}，{nm}在{['窗边记录今天的思绪', '黄昏的光里写下一段话', '夜晚的灯光下整理心情'][int(d[-1])%3]}。"
        f"{['偶然听到一首歌，旋律像极了某个久远的午后。', '翻开日历才发现，时间真的过得比想象中快。', '今天没有特别的事，但就是莫名的心情很好。'][(int(d[-1])+2)%3]}"
        f"{mats[1]['text'] if len(mats)>1 else '就这样，安安静静地，和今天说了晚安。'}"
    ),
    # 轻文学型
    lambda d, mats, nm: (
        f"{d}。{['云在慢慢走，时间也是。', '风穿过窗缝，带来了远方的声音。', '午后的光影在地板上缓缓移动。'][int(d[-1])%3]}"
        f"{nm}今天想起了一句话：「{mats[0]['text']}」——"
        f"{['有些道理离我们很近，只是平时太忙，没空听见它们。', '把它记下来，也许未来的哪一天会再遇见它。', '这句话在今天的空气里显得格外温柔。'][(int(d[-1])+1)%3]}"
    ),
    # 俏皮元气型
    lambda d, mats, nm: (
        f"叮——{d}的{nm}报道！"
        f"{['今天也是被美食和好天气宠爱的一天呢！', '伸个大大的懒腰，和今天的自己说嗨～', '翻开今天的笔记本，发现值得记住的事真不少！'][int(d[-1])%3]}"
        f"{mats[0]['text'] if mats else '把今天的小美好收进口袋，明天拿出来晒太阳。'}"
        f"{['明天也要元气满满哦！', '今天先好好休息吧，明天见～', '每一天都是新的故事，我们一起慢慢写。'][(int(d[-1])+2)%3]}"
    ),
    # 哲理治愈型
    lambda d, mats, nm: (
        f"{d}的日记。\n\n"
        f"{nm}在想，{['幸福大概就是这些细碎的、不完美的日常。', '成长不是突然变好，而是一点一点靠近光亮。', '很多事情没有标准答案，重要的是你怎样看待它。'][int(d[-1])%3]}"
        f"{['今天学到的新功课：休息不是偷懒，是为下一段路积蓄力量。', '试着对镜子里的自己笑了一下，感觉还不错。', '有时候，「就这样也挺好」是最棒的答案。'][(int(d[-1])+1)%3]}"
        f"\n{mats[-1]['text'] if mats else '晚安，世界。'}"
    ),
]


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
        f"你叫{persona_name}。{persona_profile['identity']}"
        f"语气{persona_profile['voice']}；{persona_profile['habits']}。\n"
        f"现在写一段 150~220 字的中文日记。\n"
        f"规则：必须第一人称「我」，不要用emoji，不要列清单，不要思考过程，只输出日记正文。\n"
        f"日期：{date_text}\n素材：\n{bullets}"
    )

    try:
        text = _pollinations(prompt)
        # 检查返回内容是否包含思考过程（reasoning 或长段英文思考），有则视为失败
        if text and len(text) < 800 and not text.startswith("{") and 'reasoning' not in text[:200]:
            return text
    except (urllib.error.URLError, TimeoutError, ValueError, UnicodeDecodeError) as err:
        LOGGER.warning("Pollinations generation failed: %s", err)

    # 本地 fallback：用日期选择不同模板，确保每天日志不同
    day_seed = sum(ord(c) for c in date_text)
    template = FALLBACK_DIARY_TEMPLATES[day_seed % len(FALLBACK_DIARY_TEMPLATES)]
    return template(date_text, materials, persona_name)


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
    except (urllib.error.URLError, TimeoutError, ValueError, UnicodeDecodeError) as err:
        LOGGER.warning("Pollinations translation failed: %s", err)

    try:
        if len(chinese_text) > MAX_TRANSLATION_LENGTH:
            LOGGER.warning("Translation input truncated to %s chars for fallback API.", MAX_TRANSLATION_LENGTH)
        params = urllib.parse.urlencode({"q": chinese_text[:MAX_TRANSLATION_LENGTH], "langpair": f"zh-CN|{target_code}"})
        url = f"https://api.mymemory.translated.net/get?{params}"
        raw = _request_text(url)
        data = json.loads(raw)
        text = data.get("responseData", {}).get("translatedText", "").strip()
        if text:
            return text
    except (json.JSONDecodeError, urllib.error.URLError, TimeoutError, ValueError, UnicodeDecodeError) as err:
        LOGGER.warning("MyMemory fallback translation failed: %s", err)

    fallback_eng = [
        "Translation unavailable today, but the moonlight is still gentle.",
        "No translation service today. Let the Chinese version speak for itself.",
        "Translation is resting today. The original words carry their own warmth.",
        "The translator is on a coffee break. Perhaps some things don't need translation.",
        "Today's entry speaks only in Chinese. Some feelings are best in their original language.",
    ]
    date_hash = sum(ord(c) for c in chinese_text[:20]) if chinese_text else 0
    return fallback_eng[date_hash % len(fallback_eng)]
