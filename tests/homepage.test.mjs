import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const repoRoot = path.resolve(import.meta.dirname, "..");
const indexHtml = fs.readFileSync(path.join(repoRoot, "index.html"), "utf8");
const appJs = fs.readFileSync(path.join(repoRoot, "web", "app.js"), "utf8");
const logsJson = JSON.parse(fs.readFileSync(path.join(repoRoot, "web", "logs.json"), "utf8"));

test("homepage exposes the refreshed layout hooks", () => {
  assert.match(indexHtml, /id="theme-toggle"/);
  assert.match(indexHtml, /class="profile-panel"/);
  assert.match(indexHtml, /id="daily-records"/);
});

test("homepage uses the tracked Kiri avatar asset through a relative path", () => {
  assert.match(indexHtml, /src="\.\.?\/?assets\/images\/generated-image-1\.png"/);
});

test("homepage script persists theme selection locally", () => {
  assert.match(appJs, /localStorage/);
  assert.match(appJs, /theme-toggle/);
  assert.match(appJs, /kiri-theme/);
});

test("homepage keeps loading generated log records", () => {
  assert.ok(Array.isArray(logsJson.records));
  assert.ok(logsJson.records.length > 0);
});

test("README explains static homepage deployment and AI handoff entry", () => {
  const readme = fs.readFileSync(path.join(repoRoot, "README.md"), "utf8");
  assert.match(readme, /index\.html/);
  assert.match(readme, /静态托管|GitHub Pages/i);
  assert.match(readme, /introAI\.md/);
});

test("introAI documents key files for future agents", () => {
  const introAi = fs.readFileSync(path.join(repoRoot, "introAI.md"), "utf8");
  assert.match(introAi, /scripts\/run_daily_log\.py/);
  assert.match(introAi, /web\/app\.js/);
  assert.match(introAi, /web\/logs\.json/);
  assert.match(introAi, /index\.html/);
});
