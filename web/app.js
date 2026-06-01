// 页面核心节点：右侧记录列表、北京时间显示和主题切换按钮。
const bjTimeEl = document.getElementById("bj-time");
const recordsEl = document.getElementById("records");
const themeToggleEl = document.getElementById("theme-toggle");
const THEME_KEY = "kiri-theme";

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

function getThemeByBeijingTime(parts) {
  const hour = Number(parts.hour);
  return hour >= 6 && hour < 18 ? "day" : "night";
}

function updateThemeButton(theme) {
  themeToggleEl.textContent = theme === "night" ? "切换到白天" : "切换到黑夜";
}

// 使用北京时间推导默认主题，但一旦用户手动切换，就以 localStorage 中的偏好为准。
function applyTheme(theme) {
  document.body.dataset.theme = theme;
  updateThemeButton(theme);
}

function syncBeijingClock() {
  const parts = getBeijingParts();
  bjTimeEl.textContent = `北京时间：${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`;
  return parts;
}

function renderRecord(record) {
  const card = document.createElement("article");
  card.className = "card";

  const header = document.createElement("div");
  header.className = "card-header";

  const date = document.createElement("h4");
  date.className = "card-date";
  date.textContent = record.date;

  const language = document.createElement("span");
  language.className = "card-language";
  language.textContent = record.random_language;

  header.append(date, language);

  const mood = document.createElement("p");
  mood.className = "mood";
  mood.textContent = `心情记录：${record.mood_record}`;

  const diary = document.createElement("p");
  diary.className = "diary";
  diary.textContent = record.zh_diary;

  const logPath = document.createElement("a");
  logPath.className = "log-link";
  logPath.href = record.log_path;
  logPath.textContent = `查看原始日志：${record.log_path}`;

  card.append(header, mood, diary, logPath);
  return card;
}

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

const initialParts = syncBeijingClock();
const savedTheme = localStorage.getItem(THEME_KEY);
applyTheme(savedTheme || getThemeByBeijingTime(initialParts));

themeToggleEl.addEventListener("click", () => {
  const nextTheme = document.body.dataset.theme === "night" ? "day" : "night";
  localStorage.setItem(THEME_KEY, nextTheme);
  applyTheme(nextTheme);
});

setInterval(syncBeijingClock, 1000);
loadLogs();
