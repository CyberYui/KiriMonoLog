#!/usr/bin/env python3
"""Generate one daily KiriMonoLog entry."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from kirimonolog.ai_client import generate_chinese_log, translate_text
from kirimonolog.composer import choose_target_language, render_markdown
from kirimonolog.config import PERSONA_NAME, PERSONA_PROFILE
from kirimonolog.fetchers import gather_daily_materials
from kirimonolog.writer import build_log_path, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a multilingual KiriMonoLog markdown file.")
    parser.add_argument("--date", help="Log date in YYYY-MM-DD. Defaults to today's UTC date.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_date = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(dt.timezone.utc).date()
    repo_root = Path(args.repo_root).resolve()

    materials = gather_daily_materials()
    date_text = target_date.strftime("%Y-%m-%d")
    zh_text = generate_chinese_log(materials, date_text, PERSONA_NAME, PERSONA_PROFILE)
    lang_code, lang_name = choose_target_language()
    translated = translate_text(zh_text, lang_code, lang_name)

    markdown = render_markdown(target_date, materials, zh_text, lang_name, translated)
    output = build_log_path(repo_root, target_date)
    write_text(output, markdown)

    print(f"Generated log: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
