# Google Calendar Sync

The SYSTEM can import your upcoming Google Calendar events and Google Tasks as quests.

## How it works

The sync engine (in `system_sl/core/sync_service.py`) uses two interchangeable providers:

- **CalendarProvider** — reads upcoming calendar events
- **TasksProvider** — reads Google Tasks

Both save entries as local tasks and skip duplicates.

## Prerequisites

1. **Google Cloud project** with the Calendar API and Tasks API enabled.
2. A **credentials.json** OAuth client file downloaded from the [Google Cloud Console](https://console.cloud.google.com/).

## Setup

Place `credentials.json` in the system-sl data directory:

- Linux/macOS: `~/.config/system-sl/credentials.json`
- Windows: `%APPDATA%\system-sl\credentials.json`

On first sync you will be asked to authorize the app in your browser. The resulting tokens are cached to `token.json` in the same directory.

Scopes used (read-only):

```
https://www.googleapis.com/auth/calendar.readonly
https://www.googleapis.com/auth/tasks.readonly
```

## Running a sync

The sync runs when you launch the app and choose the sync option in the GUI, or programmatically:

```python
from system_sl.core.sync_service import GoogleSyncEngine, CalendarProvider, TasksProvider

engine = GoogleSyncEngine()
engine.execute_sync(CalendarProvider(engine.client))
engine.execute_sync(TasksProvider(engine.client))
```

Imported events and tasks are added to `tasks.json` with their deadlines preserved.
