"""Module for managing the background service orchestration engine."""

from PySide6.QtCore import QObject, QTimer
from system_sl.utils import SystemNotification
from system_sl.core import get_random_task


class BackgroundServiceController(QObject):
    """Orchestrates the background monitoring lifecycle and links business logic to the view layer."""

    def __init__(self, view: SystemNotification) -> None:
        """Configures the automation timer loop and stores the targeted view window interface.

        Args:
            view (SystemNotification): The UI window element instance to manipulate.
        """
        super().__init__()
        self.view: SystemNotification = view
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_and_render_task)
        self.timer.start(3600000)  # Fires once every hour

    def poll_and_render_task(self) -> None:
        """Queries core task modules and passes data changes directly to the UI panel."""
        task_info = get_random_task()
        if task_info:
            category, title = task_info
            self.view.display_message(category, title)