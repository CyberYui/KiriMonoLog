"""Configuration for KiriMonoLog."""

from __future__ import annotations

PERSONA_NAME = "桐雾（Kiri）"
PERSONA_PROFILE = {
    "identity": "一位温柔、细腻、略带元气的虚拟少女。",
    "voice": "句子简洁、治愈、带一点轻文学气质。",
    "habits": "会记录小确幸、天气、心情起伏与今日见闻。",
}

LANGUAGE_OPTIONS = {
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
}

POLLINATIONS_TEXT_API = "https://text.pollinations.ai"
POLLINATIONS_QUERY_PARAMS = {
    "model": "openai",
    "private": "true",
}

SOURCE_ENDPOINTS = [
    "https://v1.hitokoto.cn/?encode=json",
    "https://api.quotable.io/random",
    "https://api.adviceslip.com/advice",
    "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en",
]

FALLBACK_MATERIALS = [
    {
        "text": "雨停之后，街角的风闻起来像新的开始。",
        "source": "Fallback",
        "tag": "生活感悟",
    },
    {
        "text": "人类每分钟平均会眨眼 15 到 20 次。",
        "source": "Fallback",
        "tag": "趣味小知识",
    },
    {
        "text": "你不必一口气跑完春天，慢慢走也算在前进。",
        "source": "Fallback",
        "tag": "治愈文案",
    },
]
