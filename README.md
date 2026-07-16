# ⚔️ SL — The SYSTEM

> _"Arise, Player."_
> A CLI/GUI-based personal progression system inspired by **Solo Leveling**.
> **You define your daily quests**, and the SYSTEM keeps you on track — from your terminal or desktop.

---

## 🧭 Overview

**SL** is a lightweight command-line and desktop application that helps you build consistent habits and level up in real life. It features an AI-powered mentor, intelligent task prioritization, and a full desktop GUI.

## 📸 Preview

![Menu Launch](assets/menu_launch.webp)

_Launching of CLI menu_

![Toggle Autostart](assets/toggle_autostart.webp)

_A notification appearing on the desktop after a task is due._

---

## 🚀 Features

- 🧠 **Persona Builder**: A 10-step onboarding process that constructs your Player Profile to prioritize tasks based on your real-world ambitions.
- 📝 **Task Management**: Add, list, complete, and reorder tasks with deadlines and categories.
- 📅 **Google Calendar Sync**: Automatically import your tasks from Google Calendar and Tasks. (Note: Requires credentials.json from Google Cloud Console in the data directory).
- 🔔 **Native Notifications**: Desktop alerts styled with a "System" aesthetic using PySide6 HUD-style windows.
- 🔊 **Custom Notification Sounds**: Preview, set, and manage notification audio with duration validation.
- ⏰ **Background Reminder**: A persistent QTimer-based listener that keeps you on track.
- 🤖 **AI Chatbot**: Talk to "The System" — an AI mentor powered by LangChain and Gemini with task-aware tools, plus a friendly companion persona.
- 📊 **Priority Engine**: Mathematical gravity-based task scoring using cognitive weight, intrinsic importance, and time remaining with context-aware profiles (PRESSURE/GROWTH/RECOVERY).
- 🧮 **NLP Vectorizer**: spaCy-powered persona vector builder that converts your responses and task history into a 300-dimensional user profile with temporal decay.
- 🖥️ **Desktop GUI**: Full PySide6 application with chat panel, task windows, and onboarding wizard.
- ⚙️ **Cross-Platform Autostart**: Toggle the background service on Linux (.desktop), Windows (Registry), or macOS (LaunchAgent).
- 🛠️ **Zero-Friction Install**: A dedicated installer script for instant desktop shortcuts and global PATH access.
- 💾 **Privacy First**: Local JSON storage in platform-native config directories.

---

## 📦 Setup

### Requirements

- **Linux/Windows/macOS**: Fedora 43 KDE Plasma (tested), Windows 11 (tested)
- **Python**: ≥ 3.11, < 3.14
- **Environment Manager**: [uv](https://github.com/astral-sh/uv) (recommended).

### Installation

#### Option A: Install directly from releases

1. **Download** the ZIP file corresponding to your OS from the [Latest Release](https://github.com/sproutcake23/System-SL/releases):
   - 🪟 `system-sl-windows.zip`
   - 🐧 `system-sl-linux.zip`
2. **Unzip** the folder to a location of your choice.
3. **Run the Installer**:
   ```bash
   python install.py
   ```

#### Option B: Install from source

```bash
# Clone the repository
git clone https://github.com/sproutcake23/System-SL.git
cd System-SL

# Sync the environment and dependencies
uv sync

# Download the spaCy NLP model
uv run python -m spacy download en_core_web_md

# Activate the .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### Usage

#### Desktop GUI (Default)

```bash
# Launch the desktop application
uv run system-sl

# Or if installed globally:
system-sl
```

#### CLI Mode

```bash
# Launch the terminal interface
uv run system-cli

# Or if installed globally:
system-cli
```

#### Background Notification Service

```bash
# Start the background reminder loop
uv run system-sl --bg
```

#### Build Standalone Executable

```bash
# Build a standalone executable using PyInstaller
uv run build-sl
```

#### Using Desktop Shortcuts

If installed using Option A (Installer), use the generated shortcut on your Desktop or Start Menu.

---

## 🤝 Contributing

Want to help improve the System?
Check out our [Contributing Guide](CONTRIBUTING.md) to learn how to set up the development environment and project structure.
