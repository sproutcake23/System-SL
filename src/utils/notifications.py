import webview
import threading
import time
import os
import json
from core.tasks import get_random_task


class Api:
    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    def minimize(self):
        if self.window:
            self.window.hide()


def notification_loop(api):
    while True:
        task_info = get_random_task()

        if task_info and api.window:
            category, title = task_info

            safe_category = json.dumps(f"[ {category.upper()} ]")
            safe_title = json.dumps(title)

            api.window.evaluate_js(f"""
                document.getElementById('notif-category').innerText = {safe_category};
                document.getElementById('notif-message').innerText = {safe_title};
            """)

            api.window.show()
            api.window.restore()

        time.sleep(3600)


def main():
    api = Api()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "..", "ui", "notification.html")

    window = webview.create_window(
        "Notification",
        url=os.path.abspath(html_path),
        js_api=api,
        transparent=True,
        frameless=True,
        hidden=False,
        on_top=True,
        width=800,
        height=500,
    )
    api.set_window(window)

    t = threading.Thread(target=notification_loop, args=(api,), daemon=True)
    t.start()

    webview.start(gui="qt")


if __name__ == "__main__":
    main()
