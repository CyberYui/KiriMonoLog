<!-- 这是面向未来 AgentAI 的项目速览入口，目标是让后续改动不必重新全量梳理仓库。 -->
# KiriMonoLog AI Handoff

## 1. 项目定位

KiriMonoLog 是一个 **“AI 日志生成器 + 静态展示页”** 组合项目。

- **生成端**：Python 脚本按天生成 Kiri 的双语日志。
- **展示端**：根目录 `index.html` 读取 `web/logs.json`，展示 Kiri 头像、简介与每日记录。
- **自动化端**：GitHub Actions 每天运行生成脚本，如果内容发生变化就自动提交并推送。

如果未来 AgentAI 收到“改主页”“改日志生成逻辑”“重构目录”“重建前端”这类需求，建议先看完本文件再进入代码细节。

---

## 2. 技术栈

- **Python 3.12+**
  - 用于抓取素材、生成日志、写入 Markdown、导出网页 JSON。
- **Vanilla HTML / CSS / JavaScript**
  - 用于静态主页展示。
- **GitHub Actions**
  - 用于定时执行 `scripts/run_daily_log.py`。
- **Node 内置测试运行器**
  - 当前使用 `node --test tests/homepage.test.mjs` 做主页与文档的轻量回归检查。

项目没有引入前端框架，也没有依赖数据库或后端服务。

---

## 3. 关键文件总览

| 文件 | 作用 | 改动时注意 |
| --- | --- | --- |
| `index.html` | 主页入口，定义页面布局、Kiri 简介、记录区挂载点、主题按钮 | 保持对 `web/` 与 `assets/images/` 的相对路径引用 |
| `web/styles.css` | 主页全部视觉样式，包括白天/黑夜主题、左右分栏、记录卡片 | 修改颜色或布局时同时检查 day/night 两套变量 |
| `web/app.js` | 前端逻辑：更新时间、加载 `web/logs.json`、渲染记录卡片、保存主题偏好 | 避免破坏 `fetch("web/logs.json")` 和 `localStorage` 的主题键 |
| `web/logs.json` | 网页展示数据源，由 Python 导出生成 | 不建议手工长期维护，优先通过脚本刷新 |
| `scripts/run_daily_log.py` | 每日日志生成总入口，串起抓取、生成、翻译、写文件、导出 JSON 的完整流程 | 改动这里会影响整个项目主链路 |
| `scripts/kirimonolog/config.py` | Kiri 人设、语言选项、素材源和 AI 接口配置中心 | 改人设和风格优先看这里 |
| `scripts/kirimonolog/fetchers.py` | 从外部公开 API 拉取灵感素材 | 改素材来源或请求安全策略看这里 |
| `scripts/kirimonolog/ai_client.py` | 调用 AI 生成中文日记和翻译文本，并带 fallback 逻辑 | 网络异常、接口切换、降级策略从这里入手 |
| `scripts/kirimonolog/composer.py` | 把素材与正文排版成最终 Markdown | 需要改日志文档结构时修改这里 |
| `scripts/kirimonolog/web_exporter.py` | 从 `logs/` 目录提取网页所需字段并写出 `web/logs.json` | 改前端需要的新字段时，这里和前端要同步改 |
| `.github/workflows/daily-log.yml` | 定时执行脚本并自动提交产物 | 改执行时间、Python 版本、提交策略看这里 |
| `tests/homepage.test.mjs` | 检查主页结构、主题持久化、README 与 `introAI.md` 是否满足约定 | 首页或文档改动后优先跑这个测试 |

---

## 4. 目录结构与数据流

```text
scripts/run_daily_log.py
        │
        ├─ scripts/kirimonolog/fetchers.py
        ├─ scripts/kirimonolog/ai_client.py
        ├─ scripts/kirimonolog/composer.py
        ├─ scripts/kirimonolog/writer.py
        └─ scripts/kirimonolog/web_exporter.py
                │
                ├─ 输出 logs/YYYY/MM/YYYY-MM-DD.md
                └─ 输出 web/logs.json

index.html
        ├─ 引用 web/styles.css
        ├─ 引用 web/app.js
        └─ 引用 assets/images/generated-image-1.png
```

**生成流程：**

1. `run_daily_log.py` 解析参数并设置随机种子。
2. `fetchers.py` 获取素材，失败时回退到本地素材池。
3. `ai_client.py` 生成中文正文并翻译。
4. `composer.py` 渲染 Markdown。
5. `writer.py` 写入 `logs/`。
6. `web_exporter.py` 扫描 `logs/` 并更新 `web/logs.json`。
7. `index.html + web/app.js` 在前端把 JSON 渲染成主页卡片。

---

## 5. 当前主页逻辑

主页不是随机写死的数据展示页，而是一个围绕 `web/logs.json` 的静态阅读入口：

- 左侧固定展示 Kiri 的头像和角色标签。
- 右侧显示：
  - Kiri 的简介说明；
  - 北京时间；
  - 从 `web/logs.json.records` 渲染出的每日记录卡片。
- 右上角 `theme-toggle` 按钮负责切换白天 / 黑夜主题。
- 当前主题偏好会写入 `localStorage`，键名是 **`kiri-theme`**。

以后任何 AgentAI 如果要改主页，请优先保持这几个约束稳定：

1. `index.html` 仍然是入口文件。
2. `web/logs.json` 仍然是记录展示数据源。
3. 头像继续走相对路径资源。
4. 主题切换不要依赖服务端状态。

---

## 6. 最常见的维护入口

### 想改 Kiri 人设 / 生成语气

先看：

- `scripts/kirimonolog/config.py`
- `scripts/kirimonolog/ai_client.py`

### 想改日志 Markdown 的结构

先看：

- `scripts/kirimonolog/composer.py`
- `scripts/kirimonolog/writer.py`

### 想改主页布局、主题、卡片样式

先看：

- `index.html`
- `web/styles.css`
- `web/app.js`

### 想给前端增加新的记录字段

需要联动：

1. `scripts/kirimonolog/web_exporter.py`
2. `web/logs.json` 输出结构
3. `web/app.js`
4. 必要时更新 `tests/homepage.test.mjs`

### 想改自动化生成时间或 CI 行为

先看：

- `.github/workflows/daily-log.yml`

---

## 7. 对未来 AgentAI 的操作建议

1. **先看本文件，再看需求。**
2. 如果需求涉及生成链路，先检查 `scripts/run_daily_log.py` 是否受影响。
3. 如果需求只涉及展示层，优先限制在 `index.html`、`web/`、`assets/images/` 内。
4. 如果要做重构，不要先大拆目录；优先保住：
   - `index.html`
   - `web/logs.json`
   - `scripts/run_daily_log.py`
   - `.github/workflows/daily-log.yml`
5. 改完主页或文档后，至少运行：

```bash
node --test tests/homepage.test.mjs
```

6. 改完 Python 代码后，至少补充一次语法/执行验证，避免破坏每日自动生成链路。

---

## 8. 当前已知约束

- 项目追求 **静态可部署**，不要轻易引入复杂前端框架。
- `web/logs.json` 是展示层和生成层之间最直接的桥梁。
- 这个仓库已经有较多中文注释和文档风格，新增注释应延续这种可读性。
- 图片、JSON 等不适合加注释的文件不需要为了“全覆盖”强行注释。

---

## 9. 一句话总结

如果你是未来接手这个仓库的 AgentAI：**把 KiriMonoLog 看成“Python 负责产生日志，静态首页负责呈现日志”的双层项目**，再按“生成链路”或“展示链路”分别定位修改点，效率会最高。
