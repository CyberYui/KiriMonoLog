"""网页日志数据导出模块。"""

from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path
from typing import Any


def _extract(pattern: str, content: str) -> str:
    match = re.search(pattern, content, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _clean_html_cell(text: str) -> str:
    no_break = text.replace("<br>", "\n")
    plain = re.sub(r"<[^>]+>", "", no_break)
    return html.unescape(plain).strip()


def _parse_log(path: Path, repo_root: Path) -> dict[str, str]:
    raw = path.read_text(encoding="utf-8")
    date_text = path.stem
    zh_cell = _extract(r"<tr><td>(.*?)</td><td>", raw)
    zh_diary = _clean_html_cell(zh_cell)
    mood_record = html.unescape(_extract(r"- \*\*情绪短句\*\*：(.+?)（", raw))
    random_language = _extract(r"> 本日随机语种：\*\*(.+?)\*\*", raw)
    return {
        "date": date_text,
        "log_path": path.relative_to(repo_root).as_posix(),
        "mood_record": mood_record or "今日心情记录已归档",
        "zh_diary": zh_diary or "暂无日志内容",
        "random_language": random_language or "Unknown",
    }


def export_web_logs_data(repo_root: Path) -> Path:
    logs_root = repo_root / "logs"
    output_dir = repo_root / "web"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "logs.json"

    records: list[dict[str, str]] = []
    for path in sorted(logs_root.glob("*/*/*.md"), reverse=True):
        records.append(_parse_log(path, repo_root))

    payload: dict[str, Any] = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "records": records,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path
