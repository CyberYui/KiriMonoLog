const bjTimeEl = document.getElementById("bj-time");
const recordsEl = document.getElementById("records");

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

function applyThemeByBeijingTime() {
  const parts = getBeijingParts();
  const hour = Number(parts.hour);
  document.body.dataset.theme = hour >= 6 && hour < 18 ? "day" : "night";
  bjTimeEl.textContent = `北京时间：${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`;
}

function renderRecord(record) {
  const card = document.createElement("article");
  card.className = "card";

  const meta = document.createElement("p");
  meta.className = "meta";
  meta.textContent = `日期：${record.date}｜语种：${record.random_language}`;

  const mood = document.createElement("p");
  mood.className = "mood";
  mood.textContent = `心情记录：${record.mood_record}`;

  const diary = document.createElement("p");
  diary.className = "diary";
  diary.textContent = record.zh_diary;

  card.append(meta, mood, diary);
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
    fail.textContent = "日志数据加载失败，请稍后再试。";
    recordsEl.replaceChildren(fail);
  }
}

applyThemeByBeijingTime();
setInterval(applyThemeByBeijingTime, 1000);
loadLogs();
