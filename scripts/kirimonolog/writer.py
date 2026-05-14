"""Filesystem writer helpers."""

from __future__ import annotations

import datetime as dt
from pathlib import Path


def build_log_path(repo_root: Path, date_value: dt.date) -> Path:
    month_dir = repo_root / "logs" / f"{date_value.year}" / f"{date_value.month:02d}"
    month_dir.mkdir(parents=True, exist_ok=True)
    return month_dir / f"{date_value.isoformat()}.md"


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
