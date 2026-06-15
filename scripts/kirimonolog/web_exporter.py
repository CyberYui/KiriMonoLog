"""网页日志数据导出模块。

本模块负责扫描 logs/ 目录下的日志文件，提取关键信息并导出为 web/logs.json，
供前端主页渲染使用。

数据流：
  logs/YYYY/MM/YYYY-MM-DD.md → _parse_log() → web/logs.json

提取字段：
  - date: 日志日期（YYYY-MM-DD）
  - log_path: 相对路径（用于链接跳转）
  - mood_record: 情绪短句素材
  - zh_diary: 中文日记正文
  - translated_diary: 翻译后的日记内容
  - language_tag: 内容语种标签（格式：ZH + XX）
"""

from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path
from typing import Any

from kirimonolog.config import LEGACY_LANGUAGE_NAMES

# ── 正则表达式 ──

# 匹配双栏表格，提取中文原版和多语言版本两个单元格
# 使用非贪婪匹配 (.*?) 确保正确提取每个 <td> 的内容
ZH_TABLE_PATTERN = (
    r"## 今日心情日志（双语）\s*<table>.*?<tr><th>中文原版</th><th>多语言版本</th></tr>\s*"
    r"<tr><td>(.*?)</td><td>(.*?)</td></tr>"
)

# 匹配情绪短句素材，兼容全角（中文）和半角（英文）括号
MOOD_PATTERN = r"- \*\*情绪短句\*\*：(.+?)(?:（|\(|$)"

# 新版语言标签格式：提取 "ZH + XX" 中的语言部分
LANGUAGE_TAG_PATTERN = r"> 本日内容语种：\*\*(.+?)\*\*"

# 旧版语言标签格式：提取语言名称（如 "日本語"、"English"）
LEGACY_LANGUAGE_PATTERN = r"> 本日随机语种：\*\*(.+?)\*\*"


def _extract(pattern: str, content: str) -> str | tuple[str, str, ...]:
    """从内容中提取正则匹配值。

    根据正则中的捕获组数量返回不同值：
    - 无捕获组或匹配失败：返回空字符串 ""
    - 单个捕获组：返回匹配的字符串
    - 多个捕获组：返回匹配的字符串元组

    Args:
        pattern: 正则表达式模式
        content: 要搜索的文本内容

    Returns:
        匹配的字符串或字符串元组，匹配失败返回空字符串
    """
    match = re.search(pattern, content, flags=re.DOTALL)
    if not match:
        return ""
    # 多个捕获组时返回元组
    if match.lastindex and match.lastindex >= 2:
        return tuple(match.group(i).strip() for i in range(1, match.lastindex + 1))
    return match.group(1).strip()


def _clean_html_cell(text: str) -> str:
    """清理 HTML 单元格内容，转换为纯文本。

    处理流程：
    1. 将 <br> 标签替换为换行符
    2. 移除所有 HTML 标签
    3. 解码 HTML 实体（如 &amp; → &）
    4. 去除首尾空白

    Args:
        text: 包含 HTML 的单元格内容

    Returns:
        清理后的纯文本
    """
    no_break = text.replace("<br>", "\n")
    plain = re.sub(r"<[^>]+>", "", no_break)
    return html.unescape(plain).strip()


def _parse_language_tag(raw: str) -> str:
    """解析日志文件中的语言标签。

    兼容新旧两种格式：
    - 新版："> 本日内容语种：**ZH + JP**" → "ZH + JP"
    - 旧版："> 本日随机语种：**日本語**" → "ZH + JP"（转为短名称）

    Args:
        raw: 日志文件原始内容

    Returns:
        标准化的语言标签（格式：ZH + XX）
    """
    # 尝试匹配新版格式
    new_tag = _extract(LANGUAGE_TAG_PATTERN, raw)
    if new_tag:
        return new_tag

    # 回退到旧版格式，将语言全称转为短名称
    old_lang = _extract(LEGACY_LANGUAGE_PATTERN, raw)
    if old_lang:
        short_name = LEGACY_LANGUAGE_NAMES.get(old_lang, old_lang)
        return f"ZH + {short_name}"

    return "ZH + ?"


def _parse_log(path: Path, repo_root: Path) -> dict[str, str]:
    """解析单个日志文件，提取结构化数据。

    Args:
        path: 日志文件路径
        repo_root: 仓库根目录路径

    Returns:
        包含日期、路径、心情记录、双语日记和语言标签的字典
    """
    raw = path.read_text(encoding="utf-8")
    date_text = path.stem

    # 提取双栏表格内容
    table_cells = _extract(ZH_TABLE_PATTERN, raw)
    if isinstance(table_cells, tuple) and len(table_cells) == 2:
        zh_cell, translated_cell = table_cells
    else:
        zh_cell, translated_cell = "", ""
    zh_diary = _clean_html_cell(zh_cell)
    translated_diary = _clean_html_cell(translated_cell)
    # 提取情绪短句素材
    mood_record = html.unescape(_extract(MOOD_PATTERN, raw))

    # 解析语言标签
    language_tag = _parse_language_tag(raw)

    return {
        "date": date_text,
        "log_path": path.relative_to(repo_root).as_posix(),
        "mood_record": mood_record or "今日心情记录已归档",
        "zh_diary": zh_diary or "暂无日志内容",
        "translated_diary": translated_diary or "暂无翻译内容",
        "language_tag": language_tag,
    }


def export_web_logs_data(repo_root: Path) -> Path:
    """扫描日志目录并导出为 JSON 数据文件。

    遍历 logs/ 下所有 YYYY/MM/YYYY-MM-DD.md 文件，提取结构化数据，
    按日期降序排列，输出到 web/logs.json。

    Args:
        repo_root: 仓库根目录路径

    Returns:
        输出文件路径
    """
    logs_root = repo_root / "logs"
    output_dir = repo_root / "web"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "logs.json"

    # 按日期降序排列所有日志文件
    records: list[dict[str, str]] = []
    for path in sorted(logs_root.glob("*/*/*.md"), reverse=True):
        records.append(_parse_log(path, repo_root))

    payload: dict[str, Any] = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "records": records,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path
