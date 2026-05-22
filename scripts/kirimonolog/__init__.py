"""KiriMonoLog 核心包（Core Package）。

本包实现了 KiriMonoLog 项目的全部核心逻辑，包括：
- config.py   : 人设配置、API 端点、语言选项、备用素材库
- fetchers.py : 从免费公开 API 抓取每日素材（名言/建议/趣闻等）
- ai_client.py: 调用 AI 接口生成中文日记正文，以及多语言翻译
- composer.py : 将素材和生成的文本组合成最终的 Markdown 日志
- writer.py   : 文件系统写入辅助（构建路径、写入文件）

所有模块仅依赖 Python 标准库，无需安装第三方包。
"""
