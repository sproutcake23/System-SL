from PySide6.QtCore import QSize
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget, QListWidget
from src.core.tasks import load_data,TASKS_FILE_PATH

class TasksWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tasks")
        self.setMinimumSize(QSize(800,400))

        self.tasks_data = load_data(TASKS_FILE_PATH)

        layout = QVBoxLayout(self)

        label = QLabel("Here are your tasks!!")
        layout.addWidget(label)

        self.tasks_list_widget = QListWidget()
        layout.addWidget(self.tasks_list_widget)

        self.display_tasks()

    def display_tasks(self):
        self.tasks_list_widget.clear()
        for task_list in self.tasks_data.values():
            for task in task_list:
                title = task.get("title")
                self.tasks_list_widget.addItem(title)

