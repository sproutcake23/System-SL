from PySide6.QtCore import QDate, QSize, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.tasks import (
    add_tasks,
    load_tasks,
    mark_task_completed,
    remove_tasks,
)


class TasksWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tasks")
        self.setMinimumSize(QSize(800, 400))

        root = QVBoxLayout(self)
        root.addWidget(QLabel("Here are your tasks!!"))

        self.tasks_list_widget = QListWidget()
        root.addWidget(self.tasks_list_widget, stretch=1)

        action_row = QHBoxLayout()
        self.complete_button = QPushButton("Mark complete")
        self.complete_button.clicked.connect(self._on_complete)
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self._on_remove)
        action_row.addWidget(self.complete_button)
        action_row.addWidget(self.remove_button)
        action_row.addStretch(1)
        root.addLayout(action_row)

        root.addWidget(QLabel("Add task"))

        add_row = QHBoxLayout()
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Category")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title")

        self.deadline_checkbox = QCheckBox("Deadline:")
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDisplayFormat("yyyy-MM-dd")
        self.deadline_edit.setDate(QDate.currentDate())
        self.deadline_edit.setMinimumDate(QDate.currentDate())
        self.deadline_edit.setEnabled(False)
        self.deadline_checkbox.toggled.connect(self.deadline_edit.setEnabled)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self._on_add)
        add_row.addWidget(self.category_input)
        add_row.addWidget(self.title_input)
        add_row.addWidget(self.deadline_checkbox)
        add_row.addWidget(self.deadline_edit)
        add_row.addWidget(self.add_button)
        root.addLayout(add_row)

        self.status_label = QLabel("")
        root.addWidget(self.status_label)

        self._refresh_list()

    def showEvent(self, event):
        super().showEvent(event)
        # Re-read from disk every time the window is shown so chatbot-driven
        # mutations made while the window was hidden show up.
        self._refresh_list()

    def _refresh_list(self):
        self.tasks_list_widget.clear()
        for category, task_list in load_tasks().items():
            for task in task_list:
                title = task.get("title", "")
                deadline = task.get("deadline")
                display = f"{category}: {title}"
                if deadline:
                    display += f"  → due {deadline}"
                item = QListWidgetItem(display)
                item.setData(Qt.UserRole, (category, title))
                self.tasks_list_widget.addItem(item)

    def _selected(self):
        item = self.tasks_list_widget.currentItem()
        if item is None:
            self.status_label.setText("Select a task first.")
            return None
        return item.data(Qt.UserRole)

    def _on_complete(self):
        target = self._selected()
        if target is None:
            return
        category, title = target
        try:
            mark_task_completed(category, title)
            self.status_label.setText(f"Completed: {title}")
        except ValueError as e:
            self.status_label.setText(str(e))
        self._refresh_list()

    def _on_remove(self):
        target = self._selected()
        if target is None:
            return
        category, title = target
        try:
            remove_tasks(category, title)
            self.status_label.setText(f"Removed: {title}")
        except ValueError as e:
            self.status_label.setText(str(e))
        self._refresh_list()

    def _on_add(self):
        category = self.category_input.text().strip()
        title = self.title_input.text().strip()
        deadline = (
            self.deadline_edit.date().toString("yyyy-MM-dd")
            if self.deadline_checkbox.isChecked()
            else None
        )
        if not category or not title:
            self.status_label.setText("Category and title are required.")
            return
        try:
            add_tasks(category, title, deadline)
            self.status_label.setText(f"Added: {title}")
            self.category_input.clear()
            self.title_input.clear()
            self.deadline_checkbox.setChecked(False)
            self.deadline_edit.setDate(QDate.currentDate())
        except ValueError as e:
            self.status_label.setText(str(e))
        self._refresh_list()
