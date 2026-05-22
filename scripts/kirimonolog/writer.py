"""文件系统写入辅助模块。

提供两个简单的文件操作函数：
- build_log_path() : 根据日期构建日志文件的存储路径（自动创建中间目录）
- write_text()     : 将文本内容写入指定路径（UTF-8 编码）

日志文件按年/月分层存储，路径格式为：
  {repo_root}/logs/{YYYY}/{MM}/{YYYY-MM-DD}.md
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path


def build_log_path(repo_root: Path, date_value: dt.date) -> Path:
    """根据仓库根目录和日期构建日志文件的完整路径。

    路径结构示例：
      repo_root/logs/2026/05/2026-05-20.md

    如果中间目录（如 logs/2026/05/）不存在，会自动创建。

    Args:
        repo_root  : 仓库根目录的 Path 对象
        date_value : 日志日期

    Returns:
        日志文件的完整路径（Path 对象）
    """
    month_dir = repo_root / "logs" / f"{date_value.year}" / f"{date_value.month:02d}"
    month_dir.mkdir(parents=True, exist_ok=True)
    return month_dir / f"{date_value.isoformat()}.md"


def write_text(path: Path, content: str) -> None:
    """将文本内容以 UTF-8 编码写入指定文件。

    写入前会自动去除内容末尾的空白字符，并确保文件以换行符结尾
   （符合 POSIX 文本文件规范，也便于 git diff 阅读）。

    Args:
        path   : 目标文件路径
        content: 要写入的文本内容
    """
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
