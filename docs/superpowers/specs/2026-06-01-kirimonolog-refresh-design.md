# KiriMonoLog Refresh Design

**Date:** 2026-06-01

**Goal:** Refresh the existing KiriMonoLog project without changing its core behavior by cleaning repository noise, improving documentation, adding maintainable comments, and upgrading the homepage into a polished static two-column presentation page for Kiri.

## Scope

This design covers four linked outcomes:

1. Repository cleanup, including removal of redundant/cache files and `.gitignore` updates.
2. Documentation refresh, including a fuller `README` and a new root-level project guide file that explains key files and code responsibilities.
3. Presentation-layer enhancement for the Kiri homepage, including the provided avatar image, day/night theme switching, and a clearer layout for profile and daily logs.
4. Final verification and push of the completed changes to the GitHub remote.

This design explicitly avoids changing the project's core domain behavior or introducing a new backend service.

## Constraints

- Preserve existing project functionality.
- Keep the site statically deployable.
- Reuse the current data/content source for daily records wherever possible.
- Add comments only to files where comments are meaningful and format-safe.
- Exclude binary assets and other non-commentable artifacts from the comment pass.

## Current-State Assumptions

- The repository already contains a working KiriMonoLog project with a homepage or equivalent presentation entry point.
- Daily log content already exists somewhere in the project and should remain the source of truth.
- The project can be maintained as a static site without introducing framework-level rebuild requirements.

If the existing repository structure differs slightly, implementation should preserve the same design intent while adapting file paths to the actual layout.

## Recommended Approach

Use a conservative enhancement strategy:

- Keep the current structure unless a small targeted reorganization directly improves clarity.
- Upgrade the homepage in place rather than rewriting the project from scratch.
- Improve documentation and comments around the existing code instead of doing broad architectural refactoring.
- Normalize static assets so the provided avatar becomes a tracked project file referenced through relative paths.

This approach minimizes risk while delivering the requested polish and maintainability improvements.

## File and Content Strategy

### Repository cleanup

- Remove cache, temporary, generated, or redundant files that should not live in version control.
- Update `.gitignore` so those files stay excluded going forward.
- Keep user-authored project files even if they are old, unless they are clearly redundant to the maintained implementation.

### Documentation

- Update `README.md` to explain:
  - what the project is,
  - where the homepage lives,
  - how to run or deploy it as a static page,
  - how avatar and daily record content are sourced,
  - how to update the page after deployment.
- Add a new non-README root file, preferably `introAI.md`, that documents:
  - the main entry file,
  - style/script/data files,
  - static assets,
  - how the page composes profile information and daily record content,
  - how the important files relate to each other,
  - the project's technical choices and constraints,
  - how a future AI agent should quickly understand the project before planning changes, refactors, or rebuild work.

This root file is not just human-facing documentation. It is the project's AI handoff document so future agents can skip full re-discovery and begin from an accurate summary of structure, logic, and maintenance expectations.

### Commenting policy

- Add a short file-level comment/header where the language or file type supports it naturally.
- Add focused inline comments for non-obvious logic, data transformation, theme toggling, rendering flow, or deployment-sensitive path handling.
- Rewrite weak or outdated comments when needed.
- Avoid noisy comments that merely restate trivial code.

### Homepage enhancement

- Copy `/Users/yui/Downloads/generated-image-1.png` into a tracked project asset location.
- Render a two-column homepage layout:
  - left column for the Kiri avatar and identity block,
  - right column for the Kiri summary and daily record content.
- Add a top-right toggle for day/night themes.
- Persist the active theme in the browser so the choice survives refresh.
- Use relative asset paths so the page works in local file mode and static hosting.

## Visual and UX Design

### Layout

- Use a responsive split layout with a visual profile panel on the left and content on the right.
- Keep the right side readable for longer daily log content.
- Preserve a clean single-page experience.

### Theme system

- Provide both day and night palettes.
- Ensure readable contrast for text, cards, controls, and image framing in both themes.
- Make the theme toggle obvious but lightweight.

### Content presentation

- Present Kiri's short introduction as a compact profile block near the top of the content column.
- Present daily records as a structured content section below the introduction.
- If multiple entries already exist, keep their current source and convert them into a clearer visual list or cards without changing the underlying meaning.

## Data Flow

1. The homepage loads its existing content source for Kiri introduction and/or daily records.
2. The page references the locally stored avatar asset through a relative path.
3. The theme toggle reads the saved preference from browser storage and applies the matching theme.
4. If no saved preference exists, the page uses the default theme chosen during implementation.

No server round-trip is required for these behaviors in the static deployment path.

## Error Handling and Safety

- If the current record source is missing, implementation should fail visibly during development rather than silently fabricating replacement data.
- Asset paths should be kept relative and simple to reduce deployment breakage.
- Cleanup must avoid deleting meaningful source files; only cache/redundant/generated artifacts should be removed.

## Testing and Validation Strategy

- Inspect the repository for existing test/build commands and reuse them rather than inventing new tooling.
- For homepage behavior changes, validate:
  - avatar renders from the copied project asset,
  - the two-column layout displays correctly,
  - theme toggle changes styles and persists after reload,
  - daily record content still appears from the existing source.
- Validate documentation against the final file layout and deployment flow.
- Confirm the repository is in a clean, pushable state before the final push.

## Deliverables

The finished work should leave the repository with:

- a cleaned tracked file set,
- an updated `.gitignore`,
- an updated `README.md`,
- a new root-level AI-oriented guide file (`introAI.md` unless implementation reveals HTML is materially better),
- improved comments across meaningful source/config/text files,
- a polished Kiri homepage using the provided avatar image,
- preserved daily record functionality,
- pushed changes on the remote repository.

## Out of Scope

- Replacing the project with a different framework.
- Adding a backend, database, or CMS.
- Inventing new daily log content when project content already exists.
- Commenting binary files or other formats where comments are invalid.
