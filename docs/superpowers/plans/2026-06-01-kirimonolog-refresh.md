# KiriMonoLog Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean the repository, improve documentation and comments, upgrade the Kiri homepage, and push the finished refresh without changing the project's core behavior.

**Architecture:** Keep the project statically deployable and preserve its existing behavior while consolidating presentation changes around the homepage entry file. Add a tracked avatar asset, refresh the documentation layer, and create an AI-oriented root guide so future agents can understand the project without re-discovering the whole codebase.

**Tech Stack:** Static HTML, CSS, vanilla JavaScript, Markdown documentation, Git/GitHub

---

## File Structure

- **Modify:** `README.md` — rewrite project overview, homepage usage, deployment, and maintenance notes.
- **Modify:** `.gitignore` — ignore cache, generated, and worktree-related noise.
- **Modify:** `index.html` — preserve the homepage entry point while upgrading layout, comments, and theme behavior.
- **Create:** `assets/images/generated-image-1.png` — tracked Kiri avatar copied from `/Users/yui/Downloads/generated-image-1.png`.
- **Create:** `introAI.md` — root-level AI handoff file describing structure, logic, and maintenance expectations.
- **Create:** `tests/homepage.test.mjs` — regression checks for homepage structure, avatar path, and theme toggle behavior.
- **Modify or remove as discovered:** cache or redundant artifacts found by repository scan (for example `.DS_Store`, temporary exports, stale build output, or duplicated static artifacts that are not the maintained source).

### Task 1: Baseline scan, cleanup rules, and regression test scaffold

**Files:**
- Modify: `.gitignore`
- Create: `tests/homepage.test.mjs`
- Test: `tests/homepage.test.mjs`

- [ ] **Step 1: Write the failing test**

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');

test('homepage includes theme toggle and profile layout hooks', () => {
  assert.match(html, /data-theme-toggle|id="theme-toggle"/);
  assert.match(html, /class="[^"]*profile|id="profile-panel"/);
  assert.match(html, /class="[^"]*daily-record|id="daily-records"/);
});

test('homepage references a relative avatar asset path', () => {
  assert.match(html, /assets\/images\/generated-image-1\.png/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/homepage.test.mjs`
Expected: FAIL because the current homepage does not yet guarantee the new structure and avatar path.

- [ ] **Step 3: Write minimal implementation**

```gitignore
# macOS noise
.DS_Store

# Worktree directories
.worktrees/
worktrees/

# Common cache output
dist/
coverage/
```

```js
// Keep this file small and structural: it only verifies the entry HTML has the
// required hooks before browser-side rendering and theme logic run.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/homepage.test.mjs`
Expected: FAIL still, because homepage markup has not been updated yet. This step only verifies the test file itself runs cleanly.

- [ ] **Step 5: Commit**

```bash
git add .gitignore tests/homepage.test.mjs
git commit -m "test: add homepage refresh regression scaffold"
```

### Task 2: Upgrade the homepage with avatar, two-column layout, and theme toggle

**Files:**
- Modify: `index.html`
- Create: `assets/images/generated-image-1.png`
- Test: `tests/homepage.test.mjs`

- [ ] **Step 1: Write the failing test**

Append this test to `tests/homepage.test.mjs`:

```js
test('homepage script persists day/night theme preference', () => {
  assert.match(html, /localStorage/);
  assert.match(html, /theme-toggle|data-theme-toggle/);
  assert.match(html, /data-theme=|document\.documentElement/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/homepage.test.mjs`
Expected: FAIL because the current homepage script does not yet show the day/night persistence hooks.

- [ ] **Step 3: Write minimal implementation**

Copy the avatar file:

```bash
mkdir -p assets/images
cp /Users/yui/Downloads/generated-image-1.png assets/images/generated-image-1.png
```

Update `index.html` so the document contains:

```html
<!-- Homepage entry for Kiri's profile and daily log view. -->
<button id="theme-toggle" type="button" aria-label="Toggle theme">Theme</button>

<main class="page-shell">
  <section id="profile-panel" class="profile-panel">
    <img
      src="./assets/images/generated-image-1.png"
      alt="Kiri portrait"
      class="profile-avatar"
    />
    <h1>Kiri</h1>
    <p class="profile-tags">Creator · Recorder · Cyber city observer</p>
  </section>

  <section class="content-panel">
    <article class="intro-card">
      <h2>About Kiri</h2>
      <p>Use the existing project introduction content here.</p>
    </article>

    <section id="daily-records" class="daily-records">
      <h2>Daily Records</h2>
      <!-- Keep the existing record content source and render it here. -->
    </section>
  </section>
</main>

<script>
  const root = document.documentElement;
  const toggle = document.getElementById('theme-toggle');
  const storedTheme = localStorage.getItem('kiri-theme') || 'night';
  root.dataset.theme = storedTheme;

  toggle.addEventListener('click', () => {
    const nextTheme = root.dataset.theme === 'night' ? 'day' : 'night';
    root.dataset.theme = nextTheme;
    localStorage.setItem('kiri-theme', nextTheme);
  });
</script>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/homepage.test.mjs`
Expected: PASS for the new structure, avatar path, and theme persistence checks.

- [ ] **Step 5: Commit**

```bash
git add index.html assets/images/generated-image-1.png tests/homepage.test.mjs
git commit -m "feat: refresh homepage layout and theme toggle"
```

### Task 3: Preserve and present existing daily record content cleanly

**Files:**
- Modify: `index.html`
- Test: `tests/homepage.test.mjs`

- [ ] **Step 1: Write the failing test**

Append this test to `tests/homepage.test.mjs`:

```js
test('homepage includes a daily records section with list-friendly structure', () => {
  assert.match(html, /id="daily-records"|class="daily-records"/);
  assert.match(html, /<section[^>]*daily-records[\s\S]*<(ul|ol|article|div)/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/homepage.test.mjs`
Expected: FAIL until the existing record content is rendered with a clearer structure.

- [ ] **Step 3: Write minimal implementation**

Inside `index.html`, keep the current project's record content source intact, but render it with readable structure such as:

```html
<section id="daily-records" class="daily-records">
  <h2>Daily Records</h2>
  <div class="record-list">
    <article class="record-card">
      <h3>2026-06-01</h3>
      <p><!-- Existing record text goes here. --></p>
    </article>
  </div>
</section>
```

Add comments only where the render flow or data reuse is not obvious:

```html
<!-- Reuse the project's existing record content rather than inventing new entries. -->
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/homepage.test.mjs`
Expected: PASS with the daily records section rendered through a stable, readable container.

- [ ] **Step 5: Commit**

```bash
git add index.html tests/homepage.test.mjs
git commit -m "feat: present daily records in structured layout"
```

### Task 4: Refresh README and create the AI handoff file

**Files:**
- Modify: `README.md`
- Create: `introAI.md`
- Test: `README.md`

- [ ] **Step 1: Write the failing test**

Create a documentation smoke check:

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const readme = fs.readFileSync(new URL('../README.md', import.meta.url), 'utf8');
const introAI = fs.readFileSync(new URL('../introAI.md', import.meta.url), 'utf8');

test('README explains homepage deployment', () => {
  assert.match(readme, /deploy|deployment|静态托管|GitHub Pages/i);
  assert.match(readme, /generated-image-1\.png|avatar/i);
});

test('introAI summarizes project structure and logic', () => {
  assert.match(introAI, /project structure|目录结构|项目结构/i);
  assert.match(introAI, /theme|主题|daily record|日志/i);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/homepage.test.mjs`
Expected: FAIL until the documentation covers deployment and AI handoff content.

- [ ] **Step 3: Write minimal implementation**

Update `README.md` to include:

```md
## Homepage

The homepage is a static entry page for Kiri. Open `index.html` locally or deploy the repository to any static host.

### Deploy

1. Keep the relative asset path `./assets/images/generated-image-1.png`.
2. Upload the repository contents to a static host such as GitHub Pages.
3. Ensure `index.html` stays at the published root.
4. Update the daily records in the homepage source when content changes.
```

Create `introAI.md` with sections like:

```md
# KiriMonoLog AI Handoff

## Purpose
Explain the project to future agents so they can plan and implement changes quickly.

## Key Files
- `index.html`: homepage entry, profile panel, daily records, theme toggle.
- `README.md`: project and deployment documentation.
- `introAI.md`: AI-facing architecture and maintenance summary.
- `assets/images/generated-image-1.png`: tracked avatar asset.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/homepage.test.mjs`
Expected: PASS with README deployment coverage and introAI structural summary present.

- [ ] **Step 5: Commit**

```bash
git add README.md introAI.md tests/homepage.test.mjs
git commit -m "docs: add deployment guide and AI handoff"
```

### Task 5: Add focused file-level and code comments across maintainable text files

**Files:**
- Modify: `index.html`
- Modify: `README.md`
- Modify: `introAI.md`
- Modify: any existing project text/source/config files discovered during scan
- Test: `tests/homepage.test.mjs`

- [ ] **Step 1: Write the failing test**

Append a lightweight structural test:

```js
test('homepage keeps explanatory comments for non-obvious behavior', () => {
  assert.match(html, /<!--[^>]*theme|<!--[^>]*record|<!--[^>]*profile/i);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/homepage.test.mjs`
Expected: FAIL until `index.html` includes focused explanatory comments.

- [ ] **Step 3: Write minimal implementation**

Use concise comments like:

```html
<!-- The theme toggle writes to localStorage so static deployments keep the user's preference. -->
<!-- Reuse the existing record content here so presentation changes do not alter project data meaning. -->
```

Also add file-level comments where the format allows it naturally:

```md
<!-- This document is the long-lived AI handoff entry for future maintenance work. -->
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/homepage.test.mjs`
Expected: PASS with non-obvious behavior now explained and regression checks still green.

- [ ] **Step 5: Commit**

```bash
git add index.html README.md introAI.md tests/homepage.test.mjs
git commit -m "docs: annotate project files for maintenance"
```

### Task 6: Final cleanup, verification, and push

**Files:**
- Modify: repository tracked file set as needed
- Test: `tests/homepage.test.mjs`

- [ ] **Step 1: Write the failing test**

Create a repository cleanliness check:

```bash
git status --short
```

Expected: output is not yet clean before final cleanup and commit.

- [ ] **Step 2: Run test to verify it fails**

Run: `git status --short`
Expected: FAIL conceptually because working tree still contains unapplied changes before the final commit.

- [ ] **Step 3: Write minimal implementation**

Remove redundant/cache artifacts discovered during scan, then run:

```bash
node --test tests/homepage.test.mjs
git add -A
git commit -m "chore: finalize kirimonolog refresh"
git push origin HEAD
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
node --test tests/homepage.test.mjs
git status --short
```

Expected:
- test output: PASS
- `git status --short`: no output after commit

- [ ] **Step 5: Commit**

```bash
git push origin HEAD
```

## Self-Review

- Spec coverage: cleanup, `.gitignore`, README refresh, root AI handoff file, homepage upgrade, comments, and push are all covered by Tasks 1-6.
- Placeholder scan: removed vague "document later" language and replaced it with concrete files, commands, and snippets.
- Type consistency: theme storage uses `kiri-theme`, homepage entry remains `index.html`, avatar asset path remains `assets/images/generated-image-1.png`, and the AI handoff file remains `introAI.md`.
