#!/usr/bin/env python3
"""KiriMonoLog 每日日志生成脚本（主入口）。

本脚本是项目的核心执行入口，由 GitHub Actions 定时触发，也可在本地手动运行。
执行流程：
  1. 解析命令行参数（日期、仓库路径、随机种子）
  2. 设置随机种子（默认使用日期序数，确保同一天结果一致）
  3. 抓取当日素材（从外部 API 或备用库）
  4. 调用 AI 生成中文日记正文
  5. 随机选择目标语言并翻译
  6. 渲染 Markdown 并写入日志文件

用法：
  # 生成今天的日志
  python scripts/run_daily_log.py --repo-root .

  # 指定日期回放
  python scripts/run_daily_log.py --repo-root . --date 2026-05-14

  # 复现同一日期的随机结果（便于调试）
  python scripts/run_daily_log.py --repo-root . --date 2026-05-14 --seed 739385
"""

from __future__ import annotations

import argparse
import datetime as dt
import random
from pathlib import Path

from kirimonolog.ai_client import generate_chinese_log, translate_text
from kirimonolog.composer import choose_target_language, render_markdown
from kirimonolog.config import PERSONA_NAME, PERSONA_PROFILE
from kirimonolog.fetchers import gather_daily_materials
from kirimonolog.writer import build_log_path, write_text


def parse_args() -> argparse.Namespace:
    """解析命令行参数。

    支持的参数：
      --date      : 日志日期（YYYY-MM-DD 格式），默认为今天（UTC）
      --repo-root : 仓库根目录路径，默认为当前目录
      --seed      : 随机种子，用于复现相同的素材/语言选择（调试用）
    """
    parser = argparse.ArgumentParser(description="Generate a multilingual KiriMonoLog markdown file.")
    parser.add_argument("--date", help="Log date in YYYY-MM-DD. Defaults to today's UTC date.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--seed", type=int, help="Optional random seed for reproducible material/language selection.")
    return parser.parse_args()


def main() -> int:
    """主函数：协调各模块完成日志生成。

    Returns:
        0 表示成功
    """
    args = parse_args()

    # 确定目标日期：使用参数指定日期或今天（UTC）
    target_date = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(dt.timezone.utc).date()
    repo_root = Path(args.repo_root).resolve()

    # 设置随机种子：优先使用参数指定的种子，否则使用日期序数
    # 这样同一天不指定种子时，结果始终一致（便于 GitHub Actions 幂等执行）
    random.seed(args.seed if args.seed is not None else target_date.toordinal())

    # Step 1: 抓取当日素材
    materials = gather_daily_materials()

    # Step 2: 生成中文日记正文
    date_text = target_date.strftime("%Y-%m-%d")
    zh_text = generate_chinese_log(materials, date_text, PERSONA_NAME, PERSONA_PROFILE)

    # Step 3: 随机选择目标语言并翻译
    lang_code, lang_name = choose_target_language()
    translated = translate_text(zh_text, lang_code, lang_name)

    # Step 4: 渲染 Markdown
    markdown = render_markdown(target_date, materials, zh_text, lang_name, translated)

    # Step 5: 写入文件
    output = build_log_path(repo_root, target_date)
    write_text(output, markdown)

    print(f"Generated log: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
