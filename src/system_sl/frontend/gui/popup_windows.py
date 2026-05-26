from PySide6.QtCore import QDate, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
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

from system_sl.core.tasks import (
    add_tasks,
    mark_task_completed,
    remove_tasks,
)
from system_sl.core.prioritization import prioritize_tasks, record_reorder_feedback


# GUI-added tasks no longer carry a user-chosen category — the model assigns one
# later. Until then they land in this default bucket.
DEFAULT_CATEGORY = "general"


class ReorderableTaskList(QListWidget):
    """Task list the user can drag to re-rank.

    Emits ``reordered(moved_text, old_rank, new_rank, new_texts)`` after a drag,
    where the ranks are 1-based positions and ``new_texts`` is the full new
    order of the item labels.
    """

    reordered = Signal(str, int, int, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dropEvent(self, event):
        moved_item = self.currentItem()
        if moved_item is None:
            super().dropEvent(event)
            return
        moved_text = moved_item.text()
        old_texts = [self.item(i).text() for i in range(self.count())]
        super().dropEvent(event)
        new_texts = [self.item(i).text() for i in range(self.count())]
        if moved_text not in old_texts or moved_text not in new_texts:
            return
        old_rank = old_texts.index(moved_text) + 1
        new_rank = new_texts.index(moved_text) + 1
        if old_rank != new_rank:
            self.reordered.emit(moved_text, old_rank, new_rank, new_texts)


class TasksWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tasks")
        self.setMinimumSize(QSize(800, 400))

        # Current display order (prioritized task dicts) and a lookup from each
        # item's label back to its task dict, kept in sync by _render().
        self._order = []
        self._text_to_task = {}

        root = QVBoxLayout(self)
        root.addWidget(QLabel("Here are your tasks!!"))

        self.tasks_list_widget = ReorderableTaskList()
        self.tasks_list_widget.reordered.connect(self._on_reordered)
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
        # Re-rank from scratch via the prioritization engine, then render.
        self._order = prioritize_tasks()
        self._render(self._order)

    def _render(self, tasks):
        """Render ``tasks`` (ordered list of dicts) as a numbered list."""
        self.tasks_list_widget.clear()
        self._text_to_task = {}
        for rank, task in enumerate(tasks, start=1):
            task["rank"] = rank
            title = task.get("title", "")
            deadline = task.get("deadline")
            display = f"{rank}. {title}"
            if deadline:
                display += f"  → due {deadline}"
            item = QListWidgetItem(display)
            # Keep (category, title) so complete/remove still address the right
            # task even though the category is no longer shown.
            item.setData(Qt.UserRole, (task.get("category", ""), title))
            self.tasks_list_widget.addItem(item)
            self._text_to_task[display] = task

    def _on_reordered(self, moved_text, old_rank, new_rank, new_texts):
        # A manual drag changes display order only — it does NOT re-run the
        # prioritization sort. Capture the feedback, then re-render in the
        # user's chosen order (renumbering + refreshing item data).
        new_order_dicts = [self._text_to_task[t] for t in new_texts if t in self._text_to_task]
        moved = self._text_to_task.get(moved_text)
        if moved is None or len(new_order_dicts) != len(new_texts):
            self._render(self._order)
            return

        moved_title = moved.get("title", "")
        new_order = [t.get("title", "") for t in new_order_dicts]
        feedback = record_reorder_feedback(moved_title, old_rank, new_rank, new_order)

        self._order = new_order_dicts
        self._render(self._order)
        self.status_label.setText(
            f"Reordered '{feedback['moved_title']}': rank "
            f"{feedback['old_rank']} → {feedback['new_rank']}"
        )

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
        title = self.title_input.text().strip()
        deadline = (
            self.deadline_edit.date().toString("yyyy-MM-dd")
            if self.deadline_checkbox.isChecked()
            else None
        )
        if not title:
            self.status_label.setText("Title is required.")
            return
        try:
            # Category is assigned by the model later; default for now.
            add_tasks(DEFAULT_CATEGORY, title, deadline)
            self.status_label.setText(f"Added: {title}")
            self.title_input.clear()
            self.deadline_checkbox.setChecked(False)
            self.deadline_edit.setDate(QDate.currentDate())
        except ValueError as e:
            self.status_label.setText(str(e))
        self._refresh_list()
