/**
 * KiriMonoLog 前端交互模块
 *
 * 功能：
 * 1. 实时显示北京时间
 * 2. 加载 web/logs.json 并渲染每日记录卡片
 * 3. 支持白天/黑夜主题切换（偏好保存在 localStorage）
 * 4. 双语日记分栏显示（中文 + 翻译版本）
 */

// 语言短名称到全称映射（用于显示翻译部分的语言标签）
const SHORT_TO_FULL_NAME = {
  EN: "English",
  JP: "日本語",
  KO: "한국어",
  ZH: "中文",
};

// 页面核心节点
const bjTimeEl = document.getElementById("bj-time");
const recordsEl = document.getElementById("records");
const themeToggleEl = document.getElementById("theme-toggle");
const THEME_KEY = "kiri-theme";

/**
 * 获取北京时间各组成部分。
 * @returns {Object} 包含 year, month, day, hour, minute, second 的对象
 */
function getBeijingParts() {
  const fmt = new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false
  });
  const parts = Object.fromEntries(fmt.formatToParts(new Date()).map((p) => [p.type, p.value]));
  return parts;
}

/**
 * 根据北京时间判断应该使用白天还是黑夜主题。
 * 6:00-18:00 为白天，其余时间为黑夜。
 * @param {Object} parts - 北京时间组成部分
 * @returns {"day" | "night"} 主题名称
 */
function getThemeByBeijingTime(parts) {
  const hour = Number(parts.hour);
  return hour >= 6 && hour < 18 ? "day" : "night";
}

/**
 * 更新主题切换按钮的文本。
 * @param {string} theme - 当前主题（"day" 或 "night"）
 */
function updateThemeButton(theme) {
  themeToggleEl.textContent = theme === "night" ? "切换到白天" : "切换到黑夜";
}

/**
 * 应用主题到页面。
 * 使用北京时间推导默认主题，但一旦用户手动切换，就以 localStorage 中的偏好为准。
 * @param {string} theme - 主题名称（"day" 或 "night"）
 */
function applyTheme(theme) {
  document.body.dataset.theme = theme;
  updateThemeButton(theme);
}

/**
 * 同步北京时间显示。
 * @returns {Object} 北京时间组成部分
 */
function syncBeijingClock() {
  const parts = getBeijingParts();
  bjTimeEl.textContent = `北京时间：${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`;
  return parts;
}

/**
 * 从语言标签中提取翻译语言短名称，并转为全称。
 * 例如："ZH + JP" → "日本語"
 * @param {string} languageTag - 语言标签（格式：ZH + XX）
 * @returns {string} 语言全称
 */
function getLanguageFullName(languageTag) {
  const shortName = languageTag.replace("ZH + ", "");
  return SHORT_TO_FULL_NAME[shortName] || shortName;
}

/**
 * 渲染单条记录卡片。
 * 卡片结构：
 * - 头部：日期 + 语言标签
 * - 心情记录
 * - 双语内容区：中文原版 + 多语言版本
 * - 查看原始日志链接
 * @param {Object} record - 记录对象
 * @returns {HTMLElement} 卡片元素
 */
function renderRecord(record) {
  const card = document.createElement("article");
  card.className = "card";

  // 头部：日期 + 语言标签
  const header = document.createElement("div");
  header.className = "card-header";

  const date = document.createElement("h4");
  date.className = "card-date";
  date.textContent = record.date;

  const language = document.createElement("span");
  language.className = "card-language";
  language.textContent = record.language_tag;

  header.append(date, language);

  // 心情记录
  const mood = document.createElement("p");
  mood.className = "mood";
  mood.textContent = `心情记录：${record.mood_record}`;

  // 双语显示区域：中文原版 + 多语言版本
  const bilingualContainer = document.createElement("div");
  bilingualContainer.className = "bilingual";

  // 中文部分
  const zhSection = document.createElement("div");
  zhSection.className = "bilingual-section";
  const zhLabel = document.createElement("span");
  zhLabel.className = "bilingual-label";
  zhLabel.textContent = "中文";
  const zhContent = document.createElement("p");
  zhContent.className = "diary";
  zhContent.textContent = record.zh_diary;
  zhSection.append(zhLabel, zhContent);

  // 翻译部分
  const translatedSection = document.createElement("div");
  translatedSection.className = "bilingual-section";
  const translatedLabel = document.createElement("span");
  translatedLabel.className = "bilingual-label";
  translatedLabel.textContent = getLanguageFullName(record.language_tag);
  const translatedContent = document.createElement("p");
  translatedContent.className = "diary";
  translatedContent.textContent = record.translated_diary;
  translatedSection.append(translatedLabel, translatedContent);

  bilingualContainer.append(zhSection, translatedSection);

  // 查看原始日志链接
  const logPath = document.createElement("a");
  logPath.className = "log-link";
  logPath.href = record.log_path;
  logPath.textContent = `查看原始日志：${record.log_path}`;

  card.append(header, mood, bilingualContainer, logPath);
  return card;
}

/**
 * 加载日志数据并渲染记录列表。
 * 从 web/logs.json 获取数据，按日期降序渲染卡片。
 */
async function loadLogs() {
  try {
    const resp = await fetch("web/logs.json", { cache: "no-store" });
    if (!resp.ok) {
      throw new Error("加载失败");
    }
    const data = await resp.json();
    recordsEl.replaceChildren(...(data.records || []).map(renderRecord));
  } catch (err) {
    const fail = document.createElement("p");
    fail.className = "load-error";
    fail.textContent = "日志数据加载失败，请稍后再试。";
    recordsEl.replaceChildren(fail);
  }
}

// 初始化：同步时钟、应用主题、设置定时器
const initialParts = syncBeijingClock();
const savedTheme = localStorage.getItem(THEME_KEY);
applyTheme(savedTheme || getThemeByBeijingTime(initialParts));

// 主题切换事件
themeToggleEl.addEventListener("click", () => {
  const nextTheme = document.body.dataset.theme === "night" ? "day" : "night";
  localStorage.setItem(THEME_KEY, nextTheme);
  applyTheme(nextTheme);
});

// 每秒更新时钟
setInterval(syncBeijingClock, 1000);

// 加载日志数据
loadLogs();
