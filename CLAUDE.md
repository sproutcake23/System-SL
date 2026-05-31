# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**System-SL** — a Solo Leveling–themed personal task manager. Stores tasks in JSON under the OS-appropriate user config dir, optionally syncs from Google Calendar/Tasks, and shows desktop notifications. The codebase is mid-transition into a single `system_sl` package (under `src/system_sl/`); the live GUI and console-script entry points both run from there.

## Commands

Dependencies are managed with [uv](https://github.com/astral-sh/uv).

```bash
uv sync                                  # install deps into .venv
source .venv/bin/activate                # Linux/macOS  (Windows: .venv\Scripts\activate)

# Run the GUI (current entry point)
uv run system-sl                         # console script -> system_sl.frontend.gui.main:main
# or, with PYTHONPATH=src:
python -m system_sl.frontend.gui.main

# Background notifier only (no menu) — what the autostart systemd unit runs:
python -m system_sl.frontend.gui.main --bg

# Build a single-file binary
uv run python build.py                   # PyInstaller, output in dist/

# End-user installer (after building)
python src/system_sl/utils/install.py    # places binary, creates shortcut, migrates credentials.json
```

There is no test suite and no linter configured.

### Known-stale invocations
- **Two source trees coexist.** The canonical code is `src/system_sl/`. Legacy flat copies still sit at `src/cli/`, `src/core/`, `src/gui/`, `src/utils/` — edit the `system_sl` versions, not these.
- `build.py` still points its PyInstaller entry at the legacy `src/cli/main.py`, while `pyproject.toml`'s console script points at `system_sl.frontend.gui.main:main`. The two disagree; the console script is the live one.

## Architecture

### Layout under `src/system_sl/`

- **`core/`** — pure data/business logic, no UI. `tasks.py` owns JSON persistence for tasks; `prioritization.py` ranks tasks (deadline urgency + persona/goal keyword boost) and persists manual drag-reordering; `sync_service.py` holds the Google sync engine; `onboarding.py`/`user_info.py` build the persona/goal profile.
- **`utils/`** — side-effect modules. `paths.py:get_tasks_file_path(filename)` is the single path helper every disk access routes through. `autostart.py:AutostartManager` writes/removes `~/.config/systemd/user/sl-notifer.service` (runs the binary with `--bg`, `Restart=always`). `notifications_ui.py:SystemNotification` is a frameless always-on-top widget. `json_client.py` (`load_data`/`save_data`), `google_api.py`, `install.py`.
- **`services/`** — `background_service.py:BackgroundServiceController` drives the hourly notifier loop (`QTimer` → `get_random_task()` → `SystemNotification.display_message`).
- **`frontend/gui/`** — PySide6 windows. `main.py:MainWindow` is the shell (and `main()` parses `--bg`); `popup_windows.py:TasksWindow` is the drag-reorderable task list. The GUI is intentionally thin — all state lives in JSON via `core`.
- **`chatbot/`** — the chat panel's LLM client/config.

### Background notifier / autostart

Enabling "Notification AutoStart" toggles a systemd user unit that relaunches the app with `--bg` and `Restart=always`. `main()` MUST branch on `--bg` to run **only** the notifier (`SystemNotification` + `BackgroundServiceController`); if it opened the main menu instead, `Restart=always` would reopen the menu on every close (an infinite loop).

### Data storage — single source of truth

All user data lives in an OS-specific config directory, **not** in the repo:

- Linux/macOS: `~/.config/system-sl/`   •   Windows: `%APPDATA%/system-sl/`

Files: `tasks.json`, `completed_tasks.json`, `task_order.json` (saved manual reorder), `user_info.json`, `persona.json`, `.setup_complete`, `credentials.json` (user-supplied Google OAuth secret), `token.json` (auto-generated on first sync).

Always route filesystem access through `get_tasks_file_path(filename)` — don't hardcode paths or read the repo's gitignored `demo-data/`.

### Task schema & ordering

`tasks.json` is `{category: [task, ...]}`, each task `{"title": str, "created_at": str, "deadline": str | None}`. `load_tasks()` auto-migrates legacy string entries to dict form and rewrites the file — reading can mutate it. `completed_tasks.json` uses a different shape (`{category: [str, ...]}`, completion date embedded).

`prioritize_tasks()` returns a flat ranked list. `task_order.json` (`{"order": [[category, title], ...]}`) stores the user's manual drag order: tasks listed there keep those positions, anything else trails in score order. `TasksWindow` calls `save_manual_order()` after a drag and re-reads on every `showEvent`.

### Import path convention

Built with `--paths=src`, so the package is imported fully qualified: `from system_sl.core.tasks import ...`, `from system_sl.utils import ...`. Match this in new code; ignore the legacy bare-`core.`/`src.` imports in the dead trees.

### Google Calendar/Tasks sync

`core/sync_service.py` (`GoogleSyncEngine`, `CalendarProvider`, `TasksProvider`) reads `credentials.json` (user generates via Google Cloud Console — see README) and caches `token.json` after the first OAuth flow. Scopes are read-only. Calendar events become category `"calendar"`, Google Tasks become category `"task"`. Duplicates (same title in same category) are silently skipped via `ValueError` in `add_tasks`.
