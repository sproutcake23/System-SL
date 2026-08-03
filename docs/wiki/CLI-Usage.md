# CLI Usage

The SYSTEM is a desktop application, but everything is driven from the command line.

## Launching the desktop app

```bash
uv run system-sl
```

Or, if installed globally:

```bash
system-sl
```

On first launch you will be prompted for your `GOOGLE_API_KEY`. Paste it when asked; it is saved to `.env` in the system-sl data directory.

## Background notifier mode

```bash
uv run system-sl --bg
```

This runs only the hourly task notifier — it never opens the main menu. This is the mode used by the autostart entry. See [Background Service](Background-Service).

## Building a standalone executable

```bash
uv run build-sl
```

Produces a one-file executable in `dist/`. See [Building and Releasing](Building-and-Releasing).

## Legacy terminal menu

An older terminal menu still ships under `src/cli/` (with `src/core/`, `src/utils/`). It offers basic task management from the console:

```bash
cd src
python -m cli.main
```

This is legacy code kept for reference; the GUI is the supported interface.
