"""Small, in-memory pet care model shared by the CLI and Streamlit UI."""
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from uuid import uuid4


@dataclass(eq=False)
class Task:
    title: str
    time: str
    due_date: date
    duration_minutes: int = 20
    priority: str = "medium"
    frequency: str = "once"
    completed: bool = False
    task_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Task title is required.")
        try:
            parsed = datetime.strptime(self.time, "%H:%M")
        except (TypeError, ValueError):
            raise ValueError("Time must use HH:MM, for example 08:30.") from None
        self.time = parsed.strftime("%H:%M")
        if not isinstance(self.due_date, date) or isinstance(self.due_date, datetime):
            raise ValueError("Due date must be a date.")
        if not isinstance(self.duration_minutes, int) or self.duration_minutes <= 0:
            raise ValueError("Duration must be a positive number of minutes.")
        if self.priority not in ("low", "medium", "high"):
            raise ValueError("Priority must be low, medium, or high.")
        if self.frequency not in ("once", "daily", "weekly"):
            raise ValueError("Frequency must be once, daily, or weekly.")


@dataclass(eq=False)
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self):
        if not self.name.strip() or not self.species.strip():
            raise ValueError("Pet name and species are required.")

    def add_task(self, task):
        if any(item.task_id == task.task_id for item in self.tasks):
            raise ValueError("This task is already registered.")
        self.tasks.append(task)


@dataclass(eq=False)
class Owner:
    name: str
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Owner name is required.")

    def add_pet(self, pet):
        if any(item.name.casefold() == pet.name.casefold() for item in self.pets):
            raise ValueError("Choose a unique pet name.")
        self.pets.append(pet)


class Scheduler:
    def __init__(self, owner):
        self.owner = owner

    def filter_tasks(self, pet_name=None, completed=None, day=None):
        """Return (pet, task) pairs matching all supplied filters."""
        result = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                if pet_name is not None and pet.name != pet_name:
                    continue
                if completed is not None and task.completed != completed:
                    continue
                if day is not None and task.due_date != day:
                    continue
                result.append((pet, task))
        return result

    def sort_by_time(self, tasks=None):
        """Return a new chronological list; do not mutate stored task order."""
        if tasks is None:
            tasks = self.filter_tasks()
        return sorted(tasks, key=lambda pair: (pair[1].due_date, pair[1].time))

    def detect_conflicts(self, tasks=None):
        """Warn about identical date/time slots across all pets, ignoring done tasks."""
        if tasks is None:
            tasks = self.filter_tasks(completed=False)
        occupied = {}
        warnings = []
        for pet, task in self.sort_by_time(tasks):
            if task.completed:
                continue
            slot = (task.due_date, task.time)
            label = f"{pet.name}: {task.title}"
            if slot in occupied:
                warnings.append(f"{task.due_date} {task.time}: {occupied[slot]} conflicts with {label}.")
            else:
                occupied[slot] = label
        return warnings

    def mark_task_complete(self, pet, task):
        """Complete once and create one next occurrence from its scheduled date."""
        if pet not in self.owner.pets or task not in pet.tasks:
            raise ValueError("Task must belong to a registered pet.")
        if task.completed:
            return None
        task.completed = True
        days = {"daily": 1, "weekly": 7}.get(task.frequency)
        if days is None:
            return None
        next_task = replace(task, due_date=task.due_date + timedelta(days=days),
                            completed=False, task_id=uuid4().hex)
        pet.add_task(next_task)
        return next_task

    def update_task(self, pet, task, **changes):
        """Validate an edit before replacing a pending task with the same ID."""
        if pet not in self.owner.pets or task not in pet.tasks or task.completed:
            raise ValueError("Only a registered pending task can be edited.")
        allowed = {"title", "time", "due_date", "duration_minutes", "priority", "frequency"}
        if not set(changes).issubset(allowed):
            raise ValueError("Unsupported task field.")
        edited = replace(task, **changes)
        pet.tasks[pet.tasks.index(task)] = edited
        return edited

    def build_schedule(self, day, available_minutes, pet_name=None):
        """Greedily select high priorities within a care-minute budget, then sort.

        Requested times stay fixed. Conflicts produce warnings rather than moving
        appointments. Preferences are notes only; no natural-language parsing.
        """
        if available_minutes < 0:
            raise ValueError("Available minutes cannot be negative.")
        rank = {"high": 0, "medium": 1, "low": 2}
        candidates = self.filter_tasks(pet_name=pet_name, completed=False, day=day)
        candidates = sorted(candidates, key=lambda pair: (rank[pair[1].priority], pair[1].time))
        chosen, skipped = [], []
        remaining = available_minutes
        for pet, task in candidates:
            if task.duration_minutes <= remaining:
                remaining -= task.duration_minutes
                reason = f"{task.priority} priority; {task.duration_minutes} min fits the budget"
                chosen.append((pet, task, reason))
            else:
                skipped.append((pet, task))
        chosen.sort(key=lambda item: item[1].time)
        return chosen, skipped
