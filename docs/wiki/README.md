# SL — The SYSTEM

> _"Arise, Player."_

SL is a personal progression system inspired by Solo Leveling. You define your daily quests, and the SYSTEM keeps you on track — on your desktop or from the terminal.

## Preview

![Main menu](https://github.com/sproutcake23/System-SL/blob/main/assets/main.gif?raw=true)

![Task manager](https://github.com/sproutcake23/System-SL/blob/main/assets/tasks.gif?raw=true)

![Onboarding wizard](https://github.com/sproutcake23/System-SL/blob/main/assets/onboarding.gif?raw=true)

![Chat](https://github.com/sproutcake23/System-SL/blob/main/assets/chat.gif?raw=true)

![System notification](https://github.com/sproutcake23/System-SL/blob/main/assets/notification.gif?raw=true)

## Features

- **Persona Builder** — A 10-step onboarding process that builds your Player Profile from your real-world ambitions.
- **Task Management** — Add, complete, and reorder quests with deadlines and categories.
- **Google Calendar Sync** — Import tasks from Google Calendar and Tasks.
- **Native Notifications** — Desktop alerts styled like the System, with custom notification sounds.
- **AI Chatbot** — Talk to the System, an AI mentor powered by Gemini with task-aware tools, plus a friendly companion persona.
- **Priority Engine** — Context-aware scoring (PRESSURE / GROWTH / RECOVERY) of what to work on next.
- **NLP Vectorizer** — spaCy-powered persona vectors built from your responses and task history, with temporal decay.
- **Background Reminder** — A persistent hourly notifier that keeps you on track.
- **Cross-Platform Autostart** — Register the notifier on Linux, Windows, or macOS.

## Quick Start

Requirements: Python >= 3.11 and < 3.14, and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/sproutcake23/System-SL.git
cd System-SL
uv sync
```

Launch the desktop app:

```bash
uv run system-sl
```

Run the background notifier:

```bash
uv run system-sl --bg
```

Build a standalone executable:

```bash
uv run build-sl
```

## Other pages

- [Installation](Installation)
- [Features](Features)
- [Google Calendar Sync](Google-Calendar-Sync)
- [CLI Usage](CLI-Usage)
- [Background Service](Background-Service)
- [Building and Releasing](Building-and-Releasing)
