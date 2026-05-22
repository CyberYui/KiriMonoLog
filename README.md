<div align="center">

# 🌸 KiriMonoLog

**桐雾（Kiri）的每日心情日志 —— 由 AI 自动生成的二次元治愈系日记**

[![Daily Log](https://github.com/CyberYui/KiriMonoLog/actions/workflows/daily-log.yml/badge.svg)](https://github.com/CyberYui/KiriMonoLog/actions/workflows/daily-log.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-green.svg?logo=python)](https://python.org)

</div>

---

## ✨ 项目介绍

**KiriMonoLog** 是一个二次元风格的自动化日志项目：围绕虚拟少女 **桐雾（Kiri）**，每天由 GitHub Actions 自动生成并提交一篇**双语心情日志**。

> 🌙 *"把今天的小美好收进口袋，明天拿出来晒太阳。"*
> —— 桐雾（Kiri）

---

## 🎭 人设设定

| 属性 | 描述 |
|------|------|
| **名字** | 桐雾（Kiri） |
| **定位** | 温柔细腻、略带元气的虚拟少女记录者 |
| **语气** | 轻文学、治愈、简洁自然 |
| **日志主题** | 生活感悟 · 情绪短句 · 趣味见闻 · 治愈文案 |

---

## 🚀 核心能力

1. ⏰ **每日定时触发** —— 通过 `schedule` + `workflow_dispatch` 实现自动化
2. 🌐 **联网获取素材** —— 从 Hitokoto / Quotable / AdviceSlip / Useless Facts 等免费 API 抓取
3. 🤖 **AI 生成日志** —— 调用 Pollinations 免费 AI 接口生成中文日记
4. 🌍 **多语言翻译** —— 随机生成英文 / 日文 / 韩文版本
5. 📁 **自动归档** —— 按 `logs/YYYY/MM/YYYY-MM-DD.md` 分层存储
6. 🔄 **自动提交推送** —— GitHub Actions 自动 commit & push，提交者使用触发工作流的用户账号信息
7. 🖼️ **日志展示网页** —— 内置 `index.html` 页面可展示每日日期、心情记录与北京时间日/夜主题

---

## 📂 仓库结构

```text
.
├── .github/
│   └── workflows/
│       └── daily-log.yml          # GitHub Actions 自动化工作流
├── web/
│   ├── app.js                     # 网页逻辑（北京时间与主题切换）
│   ├── styles.css                 # 网页样式（昼夜主题）
│   └── logs.json                  # 网页日志数据（自动更新）
├── logs/                          # 每日日志归档（自动生成）
│   └── 2026/
│       └── 05/
│           ├── 2026-05-14.md
│           ├── 2026-05-18.md
│           ├── 2026-05-19.md
│           └── 2026-05-20.md
├── scripts/
│   ├── run_daily_log.py           # 主入口脚本
│   └── kirimonolog/               # 核心 Python 包
│       ├── __init__.py            # 包初始化
│       ├── config.py              # 人设 / 接口 / 语言 / 素材配置
│       ├── fetchers.py            # 公共素材抓取器
│       ├── ai_client.py           # AI 生成与翻译
│       ├── composer.py            # Markdown 排版渲染
│       └── writer.py              # 文件写入工具
├── daily-log-summary.md           # 每日记录汇总（方便浏览）
├── index.html                     # Kiri 每日日志展示页
├── LICENSE                        # MIT 许可证
├── README.md                      # 本文件
└── .gitignore                     # Git 忽略规则
```

---

## ⚙️ 工作原理

```
GitHub Actions 定时触发
        │
        ▼
python scripts/run_daily_log.py
        │
        ├─ 1. 抓取素材 ──→ 外部 API（失败时回退到内置素材库）
        │
        ├─ 2. 生成中文日志 ──→ Pollinations AI（失败时使用本地模板）
        │
        ├─ 3. 翻译多语言版本 ──→ 随机选择英文/日文/韩文
        │
        ├─ 4. 渲染 Markdown ──→ 双栏表格排版
        │
        └─ 5. 写入文件 ──→ logs/YYYY/MM/YYYY-MM-DD.md
                │
                ▼
        GitHub Actions 自动 commit & push
```

---

## 🖥️ 本地运行

### 生成今天的日志

```bash
python scripts/run_daily_log.py --repo-root .
```

### 指定日期回放

```bash
python scripts/run_daily_log.py --repo-root . --date 2026-05-14
```

### 浏览 Kiri 网页日志

直接打开仓库根目录下的 `index.html` 即可查看每日日期、心情记录与北京时间主题切换效果。

### 复现同一日期的随机结果（调试用）

```bash
python scripts/run_daily_log.py --repo-root . --date 2026-05-14 --seed 739385
```

---

## 🛠️ 扩展建议

- 🎨 **丰富人设** —— 在 `scripts/kirimonolog/config.py` 中扩充更多角色字段与节日设定
- 📡 **新增素材源** —— 在 `fetchers.py` 中增加新的免费素材 API
- 🎄 **节日模板** —— 在 `composer.py` 中增加节日模板、周末模板、多角色切换
- 🌐 **更多语种** —— 在 `config.py` 的 `LANGUAGE_OPTIONS` 中增加更多语言

---

## 📜 许可证

本项目采用 [MIT 许可证](./LICENSE)，Copyright (c) 2026 Hirasawa_Yui。

---

<div align="center">

> 🌸 全项目仅依赖 Python 标准库 + GitHub Actions，无需付费密钥，便于长期挂机运行。

**[⬆ 返回顶部](#-kirimonolog)**

</div>
