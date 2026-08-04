# Building and Releasing

## Building a standalone executable

Use the provided build script:

```bash
uv run build-sl
```

This invokes PyInstaller to produce a single one-file executable named `system-sl` in `dist/`:

- `--windowed --noconsole` — no terminal window on launch
- Bundles `assets/` and the spellchecker dictionary
- Entry point: `system_sl/frontend/gui/main.py`

The result is a self-contained binary for your current OS. Build once per platform (Linux and Windows) to produce the release artifacts.

## Preparing a release

1. Bump the version in `pyproject.toml`.
2. Build for each target platform.
3. Package each executable into a zip:
   - `system-sl-linux.zip`
   - `system-sl-windows.zip`
4. Create a [GitHub Release](https://github.com/sproutcake23/System-SL/releases/new) and attach the zips.

## Development setup

```bash
uv sync
uv run system-sl
```

Run the project from source during development; use the built executable only for release artifacts.
