import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from core.tasks import add_tasks

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                print(
                    "ERROR: credentials.json not found. Please download it from Google Cloud Console."
                )
                return None
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def sync_calendar_events(max_results=10):
    print("Connecting to Google Calendar...")
    service = get_calendar_service()
    if not service:
        return

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

        try:
            add_tasks("calendar", title, deadline=deadline)
            print(f" [+] Imported: {title} (Due: {deadline})")
            count += 1
        except ValueError:
            print(f" [x] Skipped (Duplicate): {title}")

    print(f"\nSync complete. {count} new tasks added.")
