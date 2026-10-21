"""Pet care model, JSON storage, and scheduling shared by the CLI and UI."""
from dataclasses import asdict, dataclass, field, replace
import json
from pathlib import Path
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
        """Validate task details and normalize its time."""
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


    def mark_complete(self):
        """Set completion status and report whether it changed."""
        if self.completed:
            return False
        self.completed = True
        return True


@dataclass(eq=False)
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self):
        """Require basic pet details."""
        if not self.name.strip() or not self.species.strip():
            raise ValueError("Pet name and species are required.")

    def add_task(self, task):
        """Register a task once for this pet."""
        if any(item.task_id == task.task_id for item in self.tasks):
            raise ValueError("This task is already registered.")
        self.tasks.append(task)


@dataclass(eq=False)
class Owner:
    name: str
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self):
        """Require an owner name."""
        if not self.name.strip():
            raise ValueError("Owner name is required.")

    def add_pet(self, pet):
        """Register a pet with a unique name."""
        if any(item.name.casefold() == pet.name.casefold() for item in self.pets):
            raise ValueError("Choose a unique pet name.")
        self.pets.append(pet)


    def get_all_tasks(self):
        """Return (pet, task) pairs across every registered pet."""
        result = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append((pet, task))
        return result


    def save_to_json(self, path="data.json"):
        """Save all pets/tasks using ISO dates and an atomic file replacement."""
        payload = asdict(self)
        for pet in payload["pets"]:
            for task in pet["tasks"]:
                task["due_date"] = task["due_date"].isoformat()
        destination = Path(path)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(destination)

    @classmethod
    def load_from_json(cls, path="data.json"):
        """Rebuild a validated owner graph from JSON without changing the file."""
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            owner = cls(payload["name"], payload.get("preferences", ""))
            seen_ids = set()
            for pet_data in payload["pets"]:
                pet = Pet(pet_data["name"], pet_data["species"])
                owner.add_pet(pet)
                for task_data in pet_data["tasks"]:
                    details = dict(task_data)
                    details["due_date"] = date.fromisoformat(details["due_date"])
                    task = Task(**details)
                    if not isinstance(task.completed, bool):
                        raise ValueError("Completion status must be true or false.")
                    if not isinstance(task.task_id, str) or not task.task_id or task.task_id in seen_ids:
                        raise ValueError("Task IDs must be unique nonempty strings.")
                    seen_ids.add(task.task_id)
                    pet.add_task(task)
            return owner
        except (KeyError, TypeError, AttributeError, ValueError) as error:
            raise ValueError(f"Invalid PawPal data: {error}") from error


class Scheduler:
    def __init__(self, owner):
        """Connect the scheduler to one owner and all their pets."""
        self.owner = owner

    def filter_tasks(self, pet_name=None, completed=None, day=None):
        """Return (pet, task) pairs matching all supplied filters."""
        result = []
        for pet, task in self.owner.get_all_tasks():
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

    def sort_by_priority(self, tasks=None):
        """Order high, medium, low priority first, then date and time."""
        if tasks is None:
            tasks = self.filter_tasks(completed=False)
        rank = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda pair: (rank[pair[1].priority], pair[1].due_date, pair[1].time))

    def next_available_slot(self, day, duration_minutes, earliest="08:00"):
        """Find a same-day free interval across all pets, including overnight tasks."""
        if not isinstance(duration_minutes, int) or duration_minutes <= 0:
            raise ValueError("Duration must be positive whole minutes.")
        try:
            start_time = datetime.strptime(earliest, "%H:%M").time()
        except (TypeError, ValueError):
            raise ValueError("Earliest time must use HH:MM.") from None
        candidate = datetime.combine(day, start_time)
        duration = timedelta(minutes=duration_minutes)
        day_end = datetime.combine(day + timedelta(days=1), datetime.min.time())
        for pet, task in self.sort_by_time(self.filter_tasks(completed=False)):
            start = datetime.combine(task.due_date, datetime.strptime(task.time, "%H:%M").time())
            end = start + timedelta(minutes=task.duration_minutes)
            if end <= candidate:
                continue
            if candidate + duration <= start:
                break
            candidate = end
        if candidate + duration > day_end:
            return None
        return candidate.strftime("%H:%M")

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

    def mark_task_complete(self, pet, task, completion_date=None):
        """Complete once; recur one or seven days after the completion date."""
        if pet not in self.owner.pets or task not in pet.tasks:
            raise ValueError("Task must belong to a registered pet.")
        if completion_date is None:
            completion_date = date.today()
        if not isinstance(completion_date, date) or isinstance(completion_date, datetime):
            raise ValueError("Completion date must be a date.")
        if not task.mark_complete():
            return None
        days = {"daily": 1, "weekly": 7}.get(task.frequency)
        if days is None:
            return None
        next_task = replace(task, due_date=completion_date + timedelta(days=days),
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
        candidates = self.filter_tasks(pet_name=pet_name, completed=False, day=day)
        candidates = self.sort_by_priority(candidates)
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
