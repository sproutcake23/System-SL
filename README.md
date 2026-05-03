# ⚔️ SL — The SYSTEM

> _“Arise, Player.”_  
> A CLI-based personal progression system inspired by **Solo Leveling**.
> **You define your daily quests**, and the SYSTEM keeps you on track — right from your terminal.

---

## 🧭 Overview

**SL** is a lightweight command-line program that helps you build consistent habits and level up in real life.

## 📸 Preview

![Menu Launch](assets/menu_launch.webp)

_Launching of CLI menu_

![Toggle Autostart](assets/toggle_autostart.webp)

_A notification appearing on the desktop after a task is due._

---

## 🚀 Features

- 🧠 **Persona Builder**: A 10-step onboarding process that constructs your Player Profile to prioritize tasks based on your real-world ambitions.
- 📝 **Task Management**: Add, list, and complete tasks directly from the terminal.
- 📅 **Google Calendar Sync**: Automatically import your tasks. (Note: Requires credentials.json from Google Cloud Console in the data directory).
- 🔔 **Native Notifications**: Desktop alerts styled with a "System" aesthetic.
- ⏰ **Background Reminder**: A persistent listener that keeps you on track.
- ⚙️ **Integrated Autostart**: Toggle the background service directly from the CLI menu.
- 🛠️ **Zero-Friction Install**: A dedicated installer script for instant desktop shortcuts and global PATH access.
- 💾 **Privacy First**: Local JSON storage

---

## 📦 Setup

### Requirements

- **Linux/Windows**: Fedora 43 KDE Plasma(tested), Windows 11(tested)
- **Python**: ≥ 3.10.
- **Environment Manager**: [uv](https://github.com/astral-sh/uv) (recommended).

### Installation

### Option A: Install directly from releases

1. **Download** the ZIP file corresponding to your OS from the [Latest Release](https://github.com/sproutcake23/System-SL/releases):
   - 🪟 `system-sl-windows.zip`
   - 🐧 `system-sl-linux.zip`
2. **Unzip** the folder to a location of your choice.
3. **Run the Installer**:
   ```bash
   python install.py
   ```

### Option B: Install from source

```bash
# Clone the repository
git clone https://github.com/sproutcake23/System-SL.git
cd System-SL

# Sync the environment and dependencies
uv sync

# Activate the .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### Usage

#### If installed from source

```bash
#to open cli menu
uv run system-sl

#for notification loop
uv run system-sl --bg
```

#### If installed using Option A (Installer)

Terminal

```bash
system-sl
```

Desktop

```text
Use the generated shortcut on your Desktop or Start Menu.
```

## 🤝 Contributing

Want to help improve the System?  
Check out our [Contributing Guide](CONTRIBUTING.md) to learn how to set up the development environment and project structure.
