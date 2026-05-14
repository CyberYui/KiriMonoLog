"""Compose multilingual markdown log content."""

from __future__ import annotations

import datetime as dt
import html
import random
from typing import Dict, List, Tuple

from kirimonolog.config import LANGUAGE_OPTIONS


Material = Dict[str, str]


def choose_target_language() -> Tuple[str, str]:
    code = random.choice(list(LANGUAGE_OPTIONS.keys()))
    return code, LANGUAGE_OPTIONS[code]


def _materials_block(materials: List[Material]) -> str:
    material_items = [f"- **{item['tag']}**：{item['text']}（{item['source']}）" for item in materials]
    return "\n".join(material_items)


def _to_html_lines(text: str) -> str:
    return "<br>".join(html.escape(line) for line in text.splitlines() if line.strip())


def render_markdown(date_value: dt.date, materials: List[Material], zh_text: str, lang_name: str, translated_text: str) -> str:
    date_str = date_value.isoformat()
    zh_html = _to_html_lines(zh_text)
    translated_html = _to_html_lines(translated_text)

    return (
        f"# {date_str} · KiriMonoLog\n\n"
        "## 今日素材\n"
        f"{_materials_block(materials)}\n\n"
        "## 今日心情日志（双语）\n"
        "<table>\n"
        "  <tr><th>中文原版</th><th>多语言版本</th></tr>\n"
        f"  <tr><td>{zh_html}</td><td>{translated_html}</td></tr>\n"
        "</table>\n\n"
        f"> 本日随机语种：**{lang_name}**\n"
    )
