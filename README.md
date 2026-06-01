<!-- 项目总览文档：同时面向维护者、部署者和未来需要快速上手的协作 Agent。 -->
<div align="center">

# 🌸 KiriMonoLog

**桐雾（Kiri）的每日心情日志 —— 由 AI 自动生成、由静态主页展示的二次元治愈系日记项目**

[![Daily Log](https://github.com/CyberYui/KiriMonoLog/actions/workflows/daily-log.yml/badge.svg)](https://github.com/CyberYui/KiriMonoLog/actions/workflows/daily-log.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-green.svg?logo=python)](https://python.org)

</div>

---

## 项目介绍

**KiriMonoLog** 是一个“生成 + 展示”一体化的静态日志项目：

1. GitHub Actions 或本地脚本每天运行 `scripts/run_daily_log.py`。
2. Python 脚本抓取公开素材、调用免费 AI 接口、生成 Kiri 的双语日志。
3. 生成结果会写入 `logs/YYYY/MM/YYYY-MM-DD.md`，并同步导出网页侧使用的 `web/logs.json`。
4. 根目录 `index.html` 作为首页入口，读取 `web/logs.json` 并展示 Kiri 的简介、头像、北京时间和每日记录。

这个仓库既能作为自动化内容生成器，也能直接作为一个可部署的静态展示页。

---

## Kiri 角色设定

| 属性 | 描述 |
| --- | --- |
| 名字 | 桐雾（Kiri） |
| 定位 | 温柔、细腻、略带元气的虚拟少女记录者 |
| 风格 | 轻文学、治愈、简洁自然 |
| 日志主题 | 生活感悟、情绪短句、趣味见闻、治愈文案 |

---

## 核心能力

1. **每日自动生成日志**：通过 `.github/workflows/daily-log.yml` 定时触发。
2. **聚合外部灵感素材**：从 Hitokoto、Quotable、AdviceSlip、Useless Facts 等公开接口抓取文本。
3. **AI 生成 Kiri 日记**：调用免费接口生成中文正文，并随机生成英文 / 日文 / 韩文版本。
4. **自动导出网页数据**：生成后同步更新 `web/logs.json`，供主页直接读取。
5. **静态网页展示**：主页支持左右分栏布局、Kiri 头像展示、北京时间显示、白天/黑夜主题切换。

---

## 目录结构

```text
.
├── .github/workflows/daily-log.yml   # 自动生成日志并推送的工作流
├── assets/images/generated-image-1.png
│                                   # Kiri 主页头像资源
├── docs/superpowers/
│   ├── specs/                      # 设计文档
│   └── plans/                      # 实施计划
├── index.html                      # 静态主页入口
├── introAI.md                      # 面向未来 AgentAI 的项目速览说明
├── scripts/
│   ├── run_daily_log.py            # 日志生成主入口
│   └── kirimonolog/                # 核心 Python 模块
├── web/
│   ├── app.js                      # 主页交互逻辑、主题切换、日志渲染
│   ├── logs.json                   # 主页读取的日志数据
│   └── styles.css                  # 主页样式
├── daily-log-summary.md            # 日志摘要索引
├── LICENSE
└── README.md
```

---

## 工作原理

```text
GitHub Actions / 手动命令
        │
        ▼
python scripts/run_daily_log.py --repo-root .
        │
        ├─ gather_daily_materials() 抓取外部素材
        ├─ generate_chinese_log() 生成中文日记
        ├─ translate_text() 生成随机语种翻译
        ├─ render_markdown() 产出 Markdown 日志
        ├─ write_text() 写入 logs/YYYY/MM/YYYY-MM-DD.md
        └─ export_web_logs_data() 导出 web/logs.json
                │
                ▼
          index.html + web/app.js
                │
                ▼
         展示 Kiri 简介与每日记录内容
```

---

## 本地运行

### 生成今天的日志

```bash
python scripts/run_daily_log.py --repo-root .
```

### 指定日期回放

```bash
python scripts/run_daily_log.py --repo-root . --date 2026-05-14
```

### 复现同一日期的随机结果

```bash
python scripts/run_daily_log.py --repo-root . --date 2026-05-14 --seed 739385
```

### 运行主页回归测试

```bash
node --test tests/homepage.test.mjs
```

---

## 主页部署与使用说明

`index.html` 是主页的唯一入口文件，依赖以下相对路径资源：

- `./web/styles.css`
- `./web/app.js`
- `./web/logs.json`
- `./assets/images/generated-image-1.png`

### 方式 1：本地预览（推荐使用静态服务器）

由于主页会通过 `fetch()` 读取 `web/logs.json`，很多浏览器在直接打开 `file://.../index.html` 时会阻止本地 JSON 读取。
因此，**本地预览的推荐方式是先启动一个轻量静态服务器**，再通过浏览器访问。

```bash
python -m http.server 8000
```

然后打开：

```text
http://localhost:8000/
```

如果你的浏览器本身允许本地 `file://` 读取同目录 JSON，那么也可以直接双击 `index.html`；但这不是跨浏览器都可靠的默认方案。

### 方式 2：部署到静态托管

这个主页适合部署到 GitHub Pages、Netlify、Vercel 静态目录或任意 Nginx/Apache 静态站点目录。

部署要点：

1. **保留根目录入口**：发布后的站点根目录应包含 `index.html`。
2. **保留相对路径结构**：`web/` 与 `assets/images/` 需要与 `index.html` 一起发布。
3. **不要改成绝对路径**：当前主页资源全部使用相对路径，便于本地打开和静态托管同时成立。
4. **更新日志后同步发布**：每次生成新日志，`web/logs.json` 也会更新；重新部署即可显示最新内容。

### 如何替换头像

1. 用新图片替换 `assets/images/generated-image-1.png`。
2. 保持文件名不变时，主页无需改代码。
3. 如果改了文件名，需要同步修改 `index.html` 中头像的 `src` 路径。

### 如何更新主页展示内容

- **Kiri 的简介**：修改 `index.html` 中 “About Kiri” 区块文本。
- **日志列表内容**：由 `web/logs.json` 提供，通常通过运行 `scripts/run_daily_log.py` 自动更新。
- **主题切换逻辑**：修改 `web/app.js`。
- **视觉风格**：修改 `web/styles.css`。

---

## 给未来维护者与 AgentAI 的建议

- 需要快速理解项目时，优先先看根目录的 **`introAI.md`**。
- 需要理解数据来源时，看 `scripts/run_daily_log.py` 和 `scripts/kirimonolog/web_exporter.py`。
- 需要调整主页样式和交互时，看 `index.html`、`web/styles.css`、`web/app.js`。
- 需要检查自动化发布时，看 `.github/workflows/daily-log.yml`。

---

## 许可证

本项目采用 [MIT 许可证](./LICENSE)。
