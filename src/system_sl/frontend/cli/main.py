import sys
import os
import glob
from PySide6.QtWidgets import QApplication

from system_sl.utils import SystemNotification
from system_sl.services import BackgroundServiceController
from system_sl.utils import AutostartManager

# from system_sl.core.calendar import sync_calendar_events , sync_google_tasks
from system_sl.core import GoogleSyncEngine, CalendarProvider, TasksProvider
from system_sl.core import (
    load_tasks,
    add_tasks,
    remove_tasks,
    get_random_task,
    mark_task_completed,
)
from system_sl.core import user_goal_check, user_edit_goal
from system_sl.core import check_and_run_onboarding, force_run_setup
from system_sl.utils.audio_manager import (
    DEFAULT_SOUNDS_DIR, get_current_sound, play_sound, 
    check_audio_duration, set_sound_setting
)

def print_menu(autostart_status):
    print(f"\n{'-' * 5}Manage your tasks{'-' * 5}")
    print("(a)Add a New Task")
    print("(s)View Tasks")
    print("(eg)Edit Goal")
    print("(ep)Edit Profile")  # Added edit profile
    print("(r)Remove a Task")
    print("(c)Task Completed")
    print("(g)Sync Google Calendar & Event")
    print(f"(as)Toggle Autostart [Current status: {autostart_status}]")
    print("(ns)To open notification sound menu")
    print("(q)Exit")
    print("-" * 27)


def add_task_mode(task_type, task_title):
    try:
        added_title = add_tasks(task_type, task_title)
        print(f"Task {task_title} is now added into the {task_type} category")
    except Exception as e:
        print(f"ERROR: {e}")


def remove_task_mode(task_type, task_title):
    try:
        removed_title = remove_tasks(task_type, task_title)
        print(f"Task {task_title} is now removed from {task_type} category")
    except Exception as e:
        print(f"ERROR: {e}")


def view_tasks(tasks):
    choice = input("(A)View All,(C)Category or (R)Random ?\n").strip().lower()
    if not tasks:
        print("No tasks found, add some tasks first")
        return

    def print_task(t):
        title = t["title"]
        deadline = t.get("deadline")
        added = t.get("created_at")

        due_str = f" | Due: {deadline}" if deadline else ""
        added_str = f" (Added: {added})" if added else ""
        print(f"  - {title}{due_str}{added_str}")

    if choice == "a":
        for category, items in tasks.items():
            print(f"\n[{category.upper()}]")
            for item in items:
                print_task(item)

    elif choice == "c":
        category = input("Enter the task category :").strip().lower()
        tasks_list = tasks.get(category)
        if tasks_list:
            print(f"Tasks listed in {category} category are :\n")
            for task in tasks_list:
                print_task(task)
        else:
            print(f"Tasks of {category} category not found")
    elif choice == "r":
        random_taskinfo = get_random_task()
        if random_taskinfo:
            cat, task = random_taskinfo
            print(f"Here is a random task:\n{task} from {cat} category")
            return
        else:
            print("No tasks found")


def task_completed(task_type, task_title):
    try:
        mark_task_completed(task_type, task_title)
        print(f"Task '{task_title}' marked as completed and moved to history.")
    except Exception as e:
        print(f"ERROR: {e}")


def inp():
    task_type = input("Enter your task type :")
    task_title = input("Enter your task title :")
    return task_type, task_title

def notification_sound_menu():
    while True:
        print(f"\n{'-' * 10} Notification Sound Menu {'-' * 10}")
        print(f"Current Sound: {os.path.basename(get_current_sound())}\n")
        
        # Load available default sounds
        if not os.path.exists(DEFAULT_SOUNDS_DIR):
            os.makedirs(DEFAULT_SOUNDS_DIR, exist_ok=True)
            
        audio_files = []
        for ext in ("*.wav", "*.mp3"):
            audio_files.extend(glob.glob(os.path.join(DEFAULT_SOUNDS_DIR, ext)))
            
        print("Available Pre-defined Sounds:")
        for idx, file_path in enumerate(audio_files, start=1):
            print(f"  [{idx}] {os.path.basename(file_path)}")
        
        print(f"  [{len(audio_files) + 1}] Add custom sound path...")
        print("\nCommands: <number> to PREVIEW | 'set <number>' to APPLY | 'q' to go BACK")
        
        choice = input("Enter command: ").strip().lower()
        
        if choice == 'q':
            break
            
        # Handle "set X" command
        if choice.startswith("set "):
            idx_str = choice.split(" ")[1]
            if idx_str.isdigit():
                idx = int(idx_str)
                if 1 <= idx <= len(audio_files):
                    set_sound_setting(audio_files[idx-1])
                    print(f"✅ Sound updated to {os.path.basename(audio_files[idx-1])}")
                    continue
        
        # Handle "X" to preview or custom path
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(audio_files):
                print(f"🔊 Playing {os.path.basename(audio_files[idx-1])}...")
                play_sound(audio_files[idx-1])
            elif idx == len(audio_files) + 1:
                custom_path = input("Enter absolute path to your .wav/.mp3 file: ").strip().strip("'\"")
                if os.path.exists(custom_path) and custom_path.lower().endswith(('.wav', '.mp3')):
                    print("Checking duration...")
                    duration_ms = check_audio_duration(custom_path)
                    
                    if duration_ms > 3000:
                        print(f"❌ REJECTED: Audio is too long ({duration_ms/1000:.1f} sec). Must be <= 3.0 seconds.")
                    elif duration_ms <= 0:
                        print("❌ Error reading audio file or file is corrupted.")
                    else:
                        print(f"🔊 Previewing custom sound ({duration_ms/1000:.1f} sec)...")
                        play_sound(custom_path)
                        confirm = input("Do you want to set this as your notification sound? (y/n): ").strip().lower()
                        if confirm == 'y':
                            set_sound_setting(custom_path)
                            print("✅ Custom sound applied!")
                else:
                    print("❌ Invalid file path or format.")
            else:
                print("Invalid number.")

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    if "--bg" in sys.argv:
        app = QApplication(sys.argv)
        window_view = SystemNotification()
        service_controller = BackgroundServiceController(window_view)
        service_controller.poll_and_render_task()
        sys.exit(app.exec())

    # ═══════════════════════════════════════════════════════════════
    # FIRST-TIME ONBOARDING - Runs ONLY on first launch
    # ═══════════════════════════════════════════════════════════════
    try:
        check_and_run_onboarding()
    except Exception as e:
        print(f"⚠️  Onboarding error: {e}")
        print("   Continuing with default settings...\n")
    
    # ═══════════════════════════════════════════════════════════════
    # Normal startup after onboarding
    # ═══════════════════════════════════════════════════════════════
    print("SYSTEM welcomes you")
    manager = AutostartManager()

    try:
        engine = GoogleSyncEngine()
        engine.execute_sync(CalendarProvider(engine.client))
        engine.execute_sync(TasksProvider(engine.client))
        user_goal_check()
    except Exception as e:
        print(f"Problem occurred while trying to connect : {e}")

    
    while True:
        status = "ON" if manager.is_enabled() else "OFF"
        print_menu(status)

        choice = input("Enter your choice :").strip().lower()
        tasks = load_tasks()

        if choice == "a":
            task_type, task_title = inp()
            add_task_mode(task_type, task_title)
        
        elif choice == "s":
            view_tasks(tasks)
        
        elif choice == "r":
            task_type, task_title = inp()
            remove_task_mode(task_type, task_title)
        
        elif choice == "c":
            task_type, task_title = inp()
            task_completed(task_type, task_title)
        
        elif choice == "g":
            try:
                sync_calendar_events()
                sync_google_tasks()
            except Exception as e:
                print(f"Problem occurred while trying to connect : {e}")
        
        elif choice == "eg":
            try:
                user_edit_goal()
            except Exception as e:
                print(f"ERROR editing the goal : {e}")

        elif choice == "as":
            if os.name == "nt":
                print("Autostart toggle is only available for linux right now\n")
                input("\nPress any key to return to menu\n")
                continue
            new_state = manager.toggle()
            print(f"Autostart is now {'ENABLED' if new_state else 'DISABLED'}")

        
        # NEW: Edit Profile command
        elif choice == "ep":
            try:
                force_run_setup()
            except Exception as e:
                print(f"ERROR editing profile : {e}")
        elif choice == "ns":
            notification_sound_menu()
            
        elif choice == "q":
            sys.exit(0)
        else:
            print("Please enter valid input")

        input("\nEnter any key to continue" + "." * 40)
        
        input("Enter any key to continue" + "." * 40)
        os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    main()
