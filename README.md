# KiriMonoLog

KiriMonoLog 是一个二次元风格的公开 GitHub 仓库模板：围绕虚拟少女 **桐雾（Kiri）**，每天由 GitHub Actions 自动生成并提交一篇双语心情日志。

## 人设设定（可持续扩展）
- 名字：桐雾（Kiri）
- 定位：温柔细腻、略带元气的虚拟少女记录者
- 语气：轻文学、治愈、简洁自然
- 日志主题：生活感悟、情绪短句、趣味见闻、治愈文案

## 核心能力
1. 每日定时触发（`schedule` + `workflow_dispatch`）；
2. 联网获取免费公开素材（Hitokoto / Quotable / AdviceSlip / Useless Facts）；
3. 调用免费公共 AI 文本接口（Pollinations）生成中文日志；
4. 随机生成一份多语言版本（英文 / 日文 / 韩文）；
5. 按 `logs/YYYY/MM/YYYY-MM-DD.md` 归档输出，清晰双栏排版；
6. 工作流自动提交并推送，形成自然贡献记录。

## 仓库结构

```text
.
├── .github/workflows/daily-log.yml
├── logs/                      # 每日日志归档（自动生成）
└── scripts/
    ├── run_daily_log.py       # 主入口
    └── kirimonolog/
        ├── config.py          # 人设/接口/语言配置
        ├── fetchers.py        # 公共素材抓取
        ├── ai_client.py       # AI生成与翻译
        ├── composer.py        # Markdown 排版
        └── writer.py          # 文件写入
```

## 工作原理
1. Action 定时执行 `python scripts/run_daily_log.py`；
2. 脚本抓取素材，失败时自动回退到内置备用素材；
3. 先生成中文原版，再随机输出英文/日文/韩文之一；
4. 写入日志文件并由 Action 自动提交推送。

## 本地运行

```bash
python scripts/run_daily_log.py --repo-root .
```

指定日期回放：

```bash
python scripts/run_daily_log.py --repo-root . --date 2026-05-14
```

复现同一日期随机结果（便于调试）：

```bash
python scripts/run_daily_log.py --repo-root . --date 2026-05-14 --seed 739385
```

## 扩展建议
- 在 `scripts/kirimonolog/config.py` 扩充更多人设字段与节日设定；
- 在 `fetchers.py` 增加新的免费素材 API；
- 在 `composer.py` 增加节日模板、周末模板、多角色切换；
- 在 `LANGUAGE_OPTIONS` 增加更多语种。

> 全项目仅依赖 Python 标准库 + GitHub Actions，无需付费密钥，便于长期挂机运行。
