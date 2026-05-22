"""AI 生成与翻译辅助模块（仅使用免费公开 API）。

本模块提供两个核心功能：
1. generate_chinese_log() —— 调用 Pollinations AI 生成中文日记正文
2. translate_text()       —— 将中文日记翻译为目标语言

降级策略（三级）：
  Pollinations（主力）→ MyMemory 翻译 API（备选）→ 内置 fallback 文案（兜底）

当 Pollinations 不可用时，generate_chinese_log 会使用本地模板生成日记，
确保即使完全离线也能产出有内容的日志。

安全机制：
- ALLOWED_AI_HOSTS 白名单限制允许请求的 AI 域名
- 对 Pollinations 返回内容进行长度和格式检查，过滤掉包含 reasoning 的异常输出
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List

from kirimonolog.config import POLLINATIONS_QUERY_PARAMS, POLLINATIONS_TEXT_API

# Material 类型别名：与 fetchers.py 中保持一致
Material = Dict[str, str]

# 允许请求的 AI 域名白名单（安全机制）
ALLOWED_AI_HOSTS = {"text.pollinations.ai", "api.mymemory.translated.net"}

# MyMemory 翻译 API 的最大输入长度限制（超出会被截断）
MAX_TRANSLATION_LENGTH = 450

# 模块级 logger，用于记录 API 调用失败等警告信息
LOGGER = logging.getLogger(__name__)


# ── 本地 Fallback 日记模板 ──
# 当 Pollinations API 不可用时，根据日期选择不同风格的模板生成日记。
# 每个模板是一个 lambda，接收 (date_text, materials, persona_name) 三个参数。
# 使用日期字符串的字符编码和来选择模板，确保同一天始终生成相同内容。
FALLBACK_DIARY_TEMPLATES = [
    # 模板 0: 温暖日常型 —— 以"今天是什么样的日子"开头，引用第一条素材，以治愈金句结尾
    lambda d, mats, nm: (
        f"今天是{d}，一个{['普普通通却让人安心的日子', '淡淡阳光洒进窗台的日子', '风很轻很轻的日子'][int(d[-1])%3]}。"
        f"{nm}翻着今天收集的小碎片，「{mats[0]['text']}」——这是我今天最想记住的一句话。"
        f"{['有时候最好的治愈，就是允许自己什么都不做。', '慢慢来，日子会自己排好队的。', '安静地度过一天，也是一种了不起的事。'][(int(d[-1])+1)%3]}"
    ),
    # 模板 1: 浪漫细腻型 —— 以"在某个场景下记录"开头，穿插心情感悟和素材引用
    lambda d, mats, nm: (
        f"{d}，{nm}在{['窗边记录今天的思绪', '黄昏的光里写下一段话', '夜晚的灯光下整理心情'][int(d[-1])%3]}。"
        f"{['偶然听到一首歌，旋律像极了某个久远的午后。', '翻开日历才发现，时间真的过得比想象中快。', '今天没有特别的事，但就是莫名的心情很好。'][(int(d[-1])+2)%3]}"
        f"{mats[1]['text'] if len(mats)>1 else '就这样，安安静静地，和今天说了晚安。'}"
    ),
    # 模板 2: 轻文学型 —— 以景物描写开头，引用素材后展开哲思
    lambda d, mats, nm: (
        f"{d}。{['云在慢慢走，时间也是。', '风穿过窗缝，带来了远方的声音。', '午后的光影在地板上缓缓移动。'][int(d[-1])%3]}"
        f"{nm}今天想起了一句话：「{mats[0]['text']}」——"
        f"{['有些道理离我们很近，只是平时太忙，没空听见它们。', '把它记下来，也许未来的哪一天会再遇见它。', '这句话在今天的空气里显得格外温柔。'][(int(d[-1])+1)%3]}"
    ),
    # 模板 3: 俏皮元气型 —— 以"叮——报道！"的活泼口吻开头，适合周末或节日
    lambda d, mats, nm: (
        f"叮——{d}的{nm}报道！"
        f"{['今天也是被美食和好天气宠爱的一天呢！', '伸个大大的懒腰，和今天的自己说嗨～', '翻开今天的笔记本，发现值得记住的事真不少！'][int(d[-1])%3]}"
        f"{mats[0]['text'] if mats else '把今天的小美好收进口袋，明天拿出来晒太阳。'}"
        f"{['明天也要元气满满哦！', '今天先好好休息吧，明天见～', '每一天都是新的故事，我们一起慢慢写。'][(int(d[-1])+2)%3]}"
    ),
    # 模板 4: 哲理治愈型 —— 以"在想"开头，探讨人生感悟，以素材金句收尾
    lambda d, mats, nm: (
        f"{d}的日记。\n\n"
        f"{nm}在想，{['幸福大概就是这些细碎的、不完美的日常。', '成长不是突然变好，而是一点一点靠近光亮。', '很多事情没有标准答案，重要的是你怎样看待它。'][int(d[-1])%3]}"
        f"{['今天学到的新功课：休息不是偷懒，是为下一段路积蓄力量。', '试着对镜子里的自己笑了一下，感觉还不错。', '有时候，「就这样也挺好」是最棒的答案。'][(int(d[-1])+1)%3]}"
        f"\n{mats[-1]['text'] if mats else '晚安，世界。'}"
    ),
]


def _request_text(url: str, timeout: int = 30) -> str:
    """发起 HTTP GET 请求并返回纯文本响应。

    Args:
        url     : 目标 URL（必须在 ALLOWED_AI_HOSTS 白名单中）
        timeout : 请求超时时间（秒），默认 30 秒

    Returns:
        响应体的纯文本内容（已去除首尾空白）

    Raises:
        ValueError: URL 域名不在白名单中
    """
    host = urllib.parse.urlparse(url).netloc
    if host not in ALLOWED_AI_HOSTS:
        raise ValueError(f"Disallowed AI host: {host}")
    request = urllib.request.Request(url, headers={"User-Agent": "KiriMonoLog/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
        return response.read().decode("utf-8", errors="replace").strip()


def _pollinations(prompt: str) -> str:
    """调用 Pollinations 文本生成 API。

    将 prompt 进行 URL 编码后拼接为 GET 请求，附加配置中的查询参数。

    Args:
        prompt: 发送给 AI 的提示词

    Returns:
        AI 生成的文本内容
    """
    encoded = urllib.parse.quote(prompt, safe="")
    query = urllib.parse.urlencode(POLLINATIONS_QUERY_PARAMS)
    url = f"{POLLINATIONS_TEXT_API}/{encoded}?{query}"
    return _request_text(url)


def _strip_tail_punctuation(text: str) -> str:
    """去除文本末尾的标点符号（中英文句号、感叹号、问号及空格）。"""
    return text.rstrip("。！？.!? ")


def generate_chinese_log(materials: List[Material], date_text: str, persona_name: str, persona_profile: dict) -> str:
    """生成中文日记正文。

    优先调用 Pollinations AI 生成，失败时回退到本地模板。

    给 AI 的 prompt 包含：
    - 人设信息（身份、语气、习惯）
    - 日期和素材列表
    - 输出要求（150~220 字、第一人称、无 emoji、无思考过程）

    Args:
        materials     : 当日素材列表（来自 gather_daily_materials）
        date_text     : 日期字符串，格式 YYYY-MM-DD
        persona_name  : 角色名称
        persona_profile: 角色人设字典（identity/voice/habits）

    Returns:
        生成的中文日记正文
    """
    # 将素材列表格式化为 bullet points，嵌入 prompt
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
        # 有效性检查：长度不超过 800、不以 { 开头（排除 JSON 响应）、前 200 字符不含 reasoning
        if text and len(text) < 800 and not text.startswith("{") and 'reasoning' not in text[:200]:
            return text
    except (urllib.error.URLError, TimeoutError, ValueError, UnicodeDecodeError) as err:
        LOGGER.warning("Pollinations generation failed: %s", err)

    # ── 降级：使用本地模板生成 ──
    # 根据日期字符串的字符编码和选择模板，确保同一天始终使用相同模板
    day_seed = sum(ord(c) for c in date_text)
    template = FALLBACK_DIARY_TEMPLATES[day_seed % len(FALLBACK_DIARY_TEMPLATES)]
    return template(date_text, materials, persona_name)


def translate_text(chinese_text: str, target_code: str, target_name: str) -> str:
    """将中文日记翻译为目标语言。

    三级降级策略：
    1. Pollinations AI 翻译（主力）
    2. MyMemory 翻译 API（备选，免费，支持中文→多语言）
    3. 内置英文 fallback 文案（兜底，仅在翻译目标为英文类时有效）

    Args:
        chinese_text: 中文日记正文
        target_code : 目标语言 ISO 639-1 代码（如 "en"/"ja"/"ko"）
        target_name : 目标语言本地名称（如 "English"/"日本語"）

    Returns:
        翻译后的文本，或 fallback 提示信息
    """
    # ── 第一级：Pollinations 翻译 ──
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

    # ── 第二级：MyMemory 翻译 API ──
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

    # ── 第三级：内置 fallback 文案 ──
    # 当所有翻译渠道都不可用时，返回一段优雅的英文提示
    fallback_eng = [
        "Translation unavailable today, but the moonlight is still gentle.",
        "No translation service today. Let the Chinese version speak for itself.",
        "Translation is resting today. The original words carry their own warmth.",
        "The translator is on a coffee break. Perhaps some things don't need translation.",
        "Today's entry speaks only in Chinese. Some feelings are best in their original language.",
    ]
    date_hash = sum(ord(c) for c in chinese_text[:20]) if chinese_text else 0
    return fallback_eng[date_hash % len(fallback_eng)]
