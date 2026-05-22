"""多语言 Markdown 日志排版模块。

本模块负责将素材数据和生成的文本组合成最终的 Markdown 日志文件。
日志采用双栏表格排版：左侧为中文原版，右侧为随机选择的多语言翻译版本。

主要函数：
- choose_target_language() : 从 LANGUAGE_OPTIONS 中随机选择一种目标语言
- render_markdown()        : 将日期、素材、中文正文、翻译文本渲染为完整 Markdown
"""

from __future__ import annotations

import datetime as dt
import html
import random
from typing import Dict, List, Tuple

from kirimonolog.config import LANGUAGE_OPTIONS

# Material 类型别名
Material = Dict[str, str]


def choose_target_language() -> Tuple[str, str]:
    """从语言选项池中随机选择一种目标语言。

    Returns:
        (语言代码, 语言名称) 的元组，如 ("en", "English")
    """
    code = random.choice(list(LANGUAGE_OPTIONS.keys()))
    return code, LANGUAGE_OPTIONS[code]


def _materials_block(materials: List[Material]) -> str:
    """将素材列表渲染为 Markdown 无序列表。

    每条素材格式为：
    - **标签**：内容文本（来源）

    使用 html.escape 防止特殊字符破坏 Markdown 格式。
    """
    material_items = [
        f"- **{html.escape(item['tag'])}**：{html.escape(item['text'])}（{html.escape(item['source'])}）"
        for item in materials
    ]
    return "\n".join(material_items)


def _to_html_lines(text: str) -> str:
    """将纯文本转换为 HTML 行（用 <br> 连接），用于表格单元格内的多行显示。

    空行会被过滤掉，每行内容经过 HTML 转义防止 XSS 或格式破坏。
    """
    return "<br>".join(html.escape(line) for line in text.splitlines() if line.strip())


def render_markdown(date_value: dt.date, materials: List[Material], zh_text: str, lang_name: str, translated_text: str) -> str:
    """渲染完整的日志 Markdown 文档。

    输出结构：
    1. 标题：# YYYY-MM-DD · KiriMonoLog
    2. 今日素材：无序列表
    3. 今日心情日志（双语）：HTML 表格，左栏中文，右栏翻译
    4. 随机语种标注

    Args:
        date_value     : 日志日期
        materials      : 当日素材列表
        zh_text        : 中文日记正文
        lang_name      : 目标语言名称（用于标注）
        translated_text: 翻译后的文本

    Returns:
        完整的 Markdown 字符串
    """
    date_str = date_value.isoformat()
    # 将纯文本转为 HTML 行，适配表格单元格内的多行排版
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
