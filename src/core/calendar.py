import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from core.tasks import add_tasks

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/tasks.readonly"
    ]


def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                print("ERROR: credentials.json not found. Please download it from Google Cloud Console.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

def format_deadline(deadline_str):
    if not deadline_str:
        return None
    
    # Handle "All-Day" calendar events which only return a date (e.g., "2026-05-10")
    if len(deadline_str) == 10:
        return f"{deadline_str} 00:00"
        
    try:
        clean_str = deadline_str.replace("Z", "+00:00")
        dt_obj = datetime.datetime.fromisoformat(clean_str)
        return dt_obj.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return deadline_str

def process_and_add_task(source_type, title, deadline):
    try:
        add_tasks(source_type, title, deadline=deadline)
        print(f" [+] Imported [{source_type}]: {title} (Due: {deadline})")
        return 1
    except ValueError:
        print(f" [x] Skipped (Duplicate): {title}")
        return 0

def sync_calendar_events(max_results=10):
    print("Connecting to Google Calendar...")
    creds = get_credentials()
    if not creds:
        return
    service = build("calendar", "v3", credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    print(f"Fetching upcoming {max_results} events...")

    try:
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
    except Exception as e:
        print(f"API Error: {e}")
        return

    if not events:
        print("No upcoming events found.")
        return

    count = 0
    for event in events:
        title = event.get("summary", "Untitled Event")
        start = event.get("start")
        deadline = start.get("dateTime", start.get("date"))
        clean_deadline = format_deadline(deadline)
        count += process_and_add_task("calendar", title, clean_deadline)
    print(f"\nSync complete. {count} new tasks added.")

def sync_google_tasks(max_results=10):
    print("Connecting to Google Tasks...")
    creds = get_credentials()
    if not creds:
        return
    
    service = build("tasks", "v1", credentials=creds)
    print(f"Fetching up to {max_results} tasks per list...")

    try:
        # Step 1: Fetch the user's task lists
        lists_result = service.tasklists().list(maxResults=10).execute()
        task_lists = lists_result.get("items", [])
    except Exception as e:
        print(f"API Error: {e}")
        return

    if not task_lists:
        print("No task lists found.")
        return

    count = 0
    for task_list in task_lists:
        try:
            tasks_result = (
                service.tasks()
                .list(
                    tasklist=task_list["id"],
                    maxResults=max_results,
                    showHidden=False,  # Set to True if you want to include completed tasks
                )
                .execute()
            )
            tasks = tasks_result.get("items", [])
        except Exception as e:
            print(f"API Error fetching list '{task_list.get('title')}': {e}")
            continue

        for task in tasks:
            title = task.get("title", "Untitled Task")
            # The Tasks API uses 'due' for deadlines, and it's formatted as an RFC 3339 timestamp
            deadline = task.get("due") 
            clean_deadline = format_deadline(deadline)
            count += process_and_add_task("task", title, clean_deadline)

    if count == 0:
        print("No new tasks found.")
    else:
        print(f"\nSync complete. {count} new tasks added.")

if __name__ == "__main__":
    sync_calendar_events()
    sync_google_tasks()
