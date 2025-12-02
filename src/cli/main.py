import sys
from src.core.tasks import load_tasks,add_tasks,remove_tasks,get_random_task,mark_task_completed
from src.core.calendar import sync_calendar_events

def print_menu():
    print(f"\n{'-'*5}Manage your tasks{'-'*5}")
    print("(a)Add a New Task")
    print("(s)View Tasks")
    print("(r)Remove a Task")
    print("(c)Task Completed")
    print("(g) Sync Google Calendar")
    print("(q)Exit")
    print("-"*27)

def add_task_mode(task_type,task_title):
    try:
        added_title = add_tasks(task_type,task_title)
        print(f"Task {task_title} is now added into the {task_type} category")
    except Exception as e:
        print(f"ERROR: {e}")
        

def remove_task_mode(task_type,task_title):
    try: 
        removed_title = remove_tasks(task_type,task_title)
        print(f"Task {task_title} is now removed from {task_type} category")
    except Exception as e:
        print(f"ERROR: {e}")
        

def view_tasks(tasks):
    choice = input("(A)View All,(C)Category or (R)Random ?\n").strip().lower()
    if not tasks:
        print("No tasks found, add some tasks first")
        return
    def print_task(t):
        # Handle display for dictionary objects
        title = t['title']
        deadline = t.get('deadline')
        added = t.get('created_at')
        
        due_str = f" | Due: {deadline}" if deadline else ""
        added_str = f" (Added: {added})" if added else ""
        print(f"  - {title}{due_str}{added_str}")

    if choice=='a':
        for category,items in tasks.items():
            print(f"\n[{category.upper()}]") 
            for item in items:
                print_task(item)

    elif choice=='c':
        category = input("Enter the task category :").strip().lower()
        tasks_list = tasks.get(category)
        if tasks_list:
            print(f"Tasks listed in {category} category are :\n")
            for task in tasks_list:
                print_task(task)
        else:
            print(f"Tasks of {category} category not found")
    elif choice=='r':
        random_taskinfo = get_random_task()
        if random_taskinfo:
            cat,task=random_taskinfo
            print(f"Here is a random task:\n{task} from {cat} category")
            return
        else:
            print("No tasks found")

def task_Completed(task_type, task_title):
    try:
        mark_task_completed(task_type, task_title)
        print(f"Task '{task_title}' marked as completed and moved to history.") 
    except Exception as e:
        print(f"ERROR: {e}")

def inp():
    task_type = input("Enter your task type :")
    task_title = input("Enter your task title :")
    return task_type,task_title
 
def main():
    print("SYSTEM welcomes you")
    while True:
        print_menu()
        choice = input("Enter your choice :").strip().lower()
        tasks = load_tasks()

        if choice=='a':
            task_type,task_title = inp()  
            add_task_mode(task_type,task_title)
        elif choice=='s':
            view_tasks(tasks)
        elif choice=='r':
            task_type,task_title = inp()           
            remove_task_mode(task_type,task_title)
        elif choice == 'c':
            task_type,task_title = inp()  
            task_Completed(task_type,task_title)
        elif choice == 'g':
            sync_calendar_events()
            
        elif choice=='q':
            sys.exit(0)
        
        else:
            print("Please enter valid input")

if __name__ == '__main__':
    main()