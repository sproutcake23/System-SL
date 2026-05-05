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
## Set Up Google Calendar & Tasks Sync
To allow System-SL to securely read your Google Calendar and Google Tasks, you need to generate a private ID card from Google called a `credentials.json` file. 

Because your data is private, Google requires you to generate this file yourself. It takes about 5 minutes, and you only have to do it once!

### Phase 1: Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and log in with your primary Google account.
2. Click the project dropdown at the top-left of the screen and click **New Project**.
3. Name the project `System-SL-Sync` (or anything you like) and click **Create**.
4. Make sure your new project is selected in the top-left dropdown.

### Phase 2: Enable the APIs
Your project needs explicit permission to talk to your Calendar and Tasks.
1. Under the Dashboard, navigate to **APIs & Services** > **Library**.
2. Search for **Google Calendar API**, click on it, and hit **Enable**.
3. Go back to the Library, search for **Google Tasks API**, click on it, and hit **Enable**.

### Phase 3: Set Up the Consent Screen
This configures the pop-up screen that asks for your permission to sync.
1. In the APIs and services, go to **APIs & Services** > **OAuth consent screen**.
2. Choose **External** and click **Create**.
3. Fill out the required fields:
   * **App name:** `System-SL`
   * **User support email:** (Your email)
   * **Developer contact info:** (Your email)
4. Click **Save and Continue** through the "Scopes" screen (you don't need to add anything here).
5. On the **Test users** screen, click **+ Add Users** and type in your own Google email address. *Note: Only emails listed here will be allowed to use your sync feature!*
6. Click **Save and Continue**.

### Phase 4: Download Your Credentials
1. In the APIs and services, click on **Credentials**.
2. Click **+ Create Credentials** at the top and select **OAuth client ID**.
3. Under "Application type," select **Desktop app**.
4. Name it `System-SL CLI` and click **Create**.
5. A pop-up will appear with your new Client ID and Secret. Click the **DOWNLOAD JSON** button.
6. Find the downloaded file on your computer, rename it to exactly **`credentials.json`**, and move it into the main `System-SL` folder where the script runs.

---

### 🚀 What to Expect on Your First Run
The first time you run the sync command in System-SL, a browser window will automatically open:
1. Google will ask you to choose your account.
2. You will see a warning screen saying **"Google hasn’t verified this app."** Don't panic! This just means you wrote the code yourself and haven't paid Google to formally review it. 
3. Click **Advanced** at the bottom, then click **Go to System-SL-Sync (unsafe)**.
4. Click **Continue/Allow** to grant access.

Once complete, you can close the browser. System-SL will automatically generate a hidden `token.json` file, and from now on, your syncs will happen quietly in the background!
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
