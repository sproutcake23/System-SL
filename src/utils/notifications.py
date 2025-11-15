import time
import sys
from plyer import notification
from src.core.tasks import get_random_task

NOTIFICATION_INTERVAL_SECONDS = 30
APP_NAME = "System-SL"

def remind_task_notification():
    task_info = get_random_task()
    if not task_info:
        return
    category,title = task_info
    notification.notify(
        title="Reminder",
        message=f"Category {category.capitalize()}\nTask: {title}",
        app_name=APP_NAME,
        timeout=5,
    )

def start_notification_daemon():
    print(f"Notification Daemon started...... {APP_NAME}")
    print(f"Interval is {NOTIFICATION_INTERVAL_SECONDS}")
    try:
        while True:
            remind_task_notification()
            time.sleep(NOTIFICATION_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("Daemon manually stopped by user ")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_notification_daemon()