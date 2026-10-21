"""Design-only skeleton retained from the full-requirements review; not app code."""
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    title: str
    time: str
    due_date: date
    duration_minutes: int = 20
    priority: str = "medium"
    frequency: str = "once"
    completed: bool = False

    def mark_complete(self):
        """Mark this activity complete."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task):
        """Store a task for this pet."""
        pass


@dataclass
class Owner:
    name: str
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet):
        """Register a pet."""
        pass

    def get_all_tasks(self):
        """Collect pet-task pairs across every pet."""
        pass


class Scheduler:
    def __init__(self, owner):
        """Use this owner's combined tasks as the scheduling source."""
        self.owner = owner

    def filter_tasks(self, pet_name=None, completed=None, day=None):
        """Select matching tasks from Owner.get_all_tasks()."""
        pass

    def sort_by_time(self, tasks=None):
        """Order tasks by date and time."""
        pass

    def mark_task_complete(self, pet, task):
        """Complete a task and create its next occurrence if recurring."""
        pass

    def detect_conflicts(self, tasks=None):
        """Return warnings for tasks scheduled at the same time."""
        pass

    def build_schedule(self, day, available_minutes, pet_name=None):
        """Choose tasks within a daily care budget."""
        pass
