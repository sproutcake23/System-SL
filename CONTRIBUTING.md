# 🤝 Contributing to SL — The SYSTEM

Thank you for your interest in contributing! This document provides an overview of the project structure and development guidelines to help you get started.

---

## 📂 Project Structure

This project follows a standard Python package layout with **SOLID principles**. Please keep this structure organized as we add new features.

```text
System-SL/
├── .gitignore
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # User-facing documentation
├── CONTRIBUTING.md             # Developer documentation (this file)
│
├── assets/                     # Images, logos, and demo GIFs
├── demo-data/                  # Sample JSON data for testing
│
└── src/
    └── system_sl/              # Main package
        │
        ├── chatbot/            # AI chatbot module
        │   ├── client.py       # ChatSession with LangChain agents
        │   ├── config.py       # Chat configuration
        │   ├── system_adi.py   # Agent definitions (mentor + friend)
        │   └── system_prompts.py # Solo Leveling persona prompts
        │
        ├── core/               # Core business logic
        │   ├── onboarding.py   # 10-step Persona Builder
        │   ├── priority_engine_new.py # Gravity-based task scoring
        │   ├── sync_service.py # Google Calendar/Tasks sync
        │   ├── tasks.py        # Task management (flat list)
        │   ├── user_info.py    # User goal management
        │   └── vector_converter.py # NLP vector builder
        │
        ├── frontend/           # User interfaces
        │   ├── cli/
        │   │   └── main.py     # Terminal menu interface
        │   └── gui/
        │       ├── main.py     # PySide6 main window
        │       ├── chat_panel.py # Chatbot panel
        │       ├── popup_windows.py # Task & onboarding windows
        │       └── theme.py    # Dynamic QSS theming
        │
        ├── services/           # Background services
        │   └── background_service.py # QTimer-based notifications
        │
        └── utils/              # Utility modules
            ├── audio_manager.py    # Notification sound system
            ├── autostart.py        # Cross-platform autostart
            ├── build.py            # PyInstaller build script
            ├── google_api.py       # Google API client
            ├── install.py          # Installer script
            ├── json_client.py      # JSON I/O utilities
            ├── notifications_ui.py # PySide6 notification HUD
            └── paths.py            # XDG-compliant path resolution
```

---

## 🛠️ Development Setup

### Prerequisites

- **Python**: ≥ 3.11, < 3.14
- **uv**: [Install uv](https://github.com/astral-sh/uv)

### Getting Started

```bash
# Clone the repository
git clone https://github.com/sproutcake23/System-SL.git
cd System-SL

# Sync dependencies
uv sync

# Download the spaCy NLP model
uv run python -m spacy download en_core_web_md

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### Running the Application

```bash
# Launch GUI
uv run system-sl

# Launch CLI
uv run system-cli

# Start background notification service
uv run system-sl --bg
```

### Building Standalone Executables

```bash
# Build using the build script
uv run build-sl
```

---

## 🧩 Module Overview

| Module | Description |
|--------|-------------|
| `chatbot/` | AI chatbot with LangChain agents and Gemini integration |
| `core/` | Business logic: onboarding, priority engine, sync, tasks, vectors |
| `frontend/cli/` | Terminal-based user interface |
| `frontend/gui/` | PySide6 desktop application |
| `services/` | Background services (notifications, autostart) |
| `utils/` | Shared utilities (paths, JSON, Google API, audio) |

---

## 📝 Code Guidelines

- Follow **SOLID principles** where applicable
- Keep modules focused and single-purpose
- Use type hints for function signatures
- Write docstrings for public functions
- Store user data in platform-native config directories (handled by `utils/paths.py`)

---

## 🐛 Reporting Issues

- Use the [GitHub Issues](https://github.com/sproutcake23/System-SL/issues) page
- Include steps to reproduce, expected behavior, and actual behavior
- Mention your OS and Python version

---

## 📬 Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Please ensure your code follows the project's style and passes any existing checks.
