from datetime import date, timedelta
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler

DAY = date(2026, 12, 31)


@pytest.fixture
def system():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    return owner, pet, Scheduler(owner)


def test_empty_schedule(system):
    _, _, scheduler = system
    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.build_schedule(DAY, 60) == ([], [])


def test_chronological_sort_is_not_in_place(system):
    _, pet, scheduler = system
    late = Task("Walk", "18:00", DAY)
    early = Task("Food", "08:00", DAY)
    tomorrow = Task("Vet", "07:00", DAY + timedelta(days=1))
    for task in [tomorrow, late, early]:
        pet.add_task(task)
    assert [task for _, task in scheduler.sort_by_time()] == [early, late, tomorrow]
    assert pet.tasks == [tomorrow, late, early]


@pytest.mark.parametrize("frequency,days", [("daily", 1), ("weekly", 7)])
def test_recurrence_rollover_and_idempotent_completion(system, frequency, days):
    _, pet, scheduler = system
    original = Task("Food", "08:00", DAY, frequency=frequency)
    pet.add_task(original)
    following = scheduler.mark_task_complete(pet, original, completion_date=DAY)
    assert original.completed
    assert following.due_date == DAY + timedelta(days=days)
    assert following.time == original.time
    assert following.frequency == frequency
    assert not following.completed
    assert following.task_id != original.task_id
    assert scheduler.mark_task_complete(pet, original, completion_date=DAY) is None
    assert len(pet.tasks) == 2


def test_once_does_not_recur(system):
    _, pet, scheduler = system
    task = Task("Vet", "12:00", DAY)
    pet.add_task(task)
    assert scheduler.mark_task_complete(pet, task) is None
    assert len(pet.tasks) == 1


def test_conflicts_across_pets_same_date_only(system):
    owner, pet, scheduler = system
    cat = Pet("Luna", "cat")
    owner.add_pet(cat)
    pet.add_task(Task("Food", "08:00", DAY))
    cat.add_task(Task("Meds", "08:00", DAY))
    cat.add_task(Task("Tomorrow", "08:00", DAY + timedelta(days=1)))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "Mochi: Food" in warnings[0] and "Luna: Meds" in warnings[0]
    scheduler.mark_task_complete(cat, cat.tasks[0])
    assert scheduler.detect_conflicts() == []


def test_same_pet_conflict(system):
    _, pet, scheduler = system
    pet.add_task(Task("Walk", "08:00", DAY))
    pet.add_task(Task("Food", "08:00", DAY))
    assert len(scheduler.detect_conflicts()) == 1


def test_combined_filters(system):
    owner, pet, scheduler = system
    other = Pet("Luna", "cat")
    owner.add_pet(other)
    task = Task("Food", "08:00", DAY)
    pet.add_task(task)
    other.add_task(Task("Play", "09:00", DAY))
    scheduler.mark_task_complete(pet, task)
    assert scheduler.filter_tasks("Mochi", True, DAY) == [(pet, task)]
    assert scheduler.filter_tasks("Mochi", False, DAY) == []
    assert scheduler.filter_tasks(day=DAY + timedelta(days=1)) == []


def test_budget_prioritizes_then_orders_and_skips(system):
    _, pet, scheduler = system
    low = Task("Play", "07:00", DAY, 20, "low")
    high = Task("Meds", "09:00", DAY, 5, "high")
    medium = Task("Brush", "08:00", DAY, 10, "medium")
    for task in [low, high, medium]:
        pet.add_task(task)
    chosen, skipped = scheduler.build_schedule(DAY, 15)
    assert [task for _, task, _ in chosen] == [medium, high]
    assert skipped == [(pet, low)]
    assert scheduler.build_schedule(DAY, 0)[0] == []
    with pytest.raises(ValueError):
        scheduler.build_schedule(DAY, -1)


def test_schedule_excludes_other_dates_completed_and_pets(system):
    owner, pet, scheduler = system
    cat = Pet("Luna", "cat")
    owner.add_pet(cat)
    pet.add_task(Task("Done", "08:00", DAY, completed=True))
    pet.add_task(Task("Tomorrow", "09:00", DAY + timedelta(days=1)))
    cat.add_task(Task("Food", "08:00", DAY))
    assert scheduler.build_schedule(DAY, 60, "Mochi") == ([], [])


@pytest.mark.parametrize("changes", [{"title": " "}, {"time": "25:00"},
    {"duration_minutes": 0}, {"priority": "urgent"}, {"frequency": "monthly"},
    {"due_date": "2026-12-31"}])
def test_invalid_task_inputs(changes):
    values = {"title": "Food", "time": "08:00", "due_date": DAY}
    values.update(changes)
    with pytest.raises(ValueError):
        Task(**values)


def test_edit_validates_without_losing_original(system):
    _, pet, scheduler = system
    task = Task("Food", "08:00", DAY)
    pet.add_task(task)
    with pytest.raises(ValueError):
        scheduler.update_task(pet, task, duration_minutes=-1)
    assert pet.tasks == [task]
    edited = scheduler.update_task(pet, task, title="Breakfast", priority="high")
    assert pet.tasks == [edited]
    assert edited.task_id == task.task_id
    assert edited.title == "Breakfast"


def test_membership_and_duplicate_guards(system):
    owner, pet, scheduler = system
    with pytest.raises(ValueError):
        owner.add_pet(Pet("mochi", "cat"))
    task = Task("Food", "08:00", DAY)
    with pytest.raises(ValueError):
        scheduler.mark_task_complete(pet, task)
    pet.add_task(task)
    with pytest.raises(ValueError):
        pet.add_task(task)


def test_task_mark_complete_changes_status():
    task = Task("Food", "08:00", DAY)
    assert task.completed is False
    assert task.mark_complete() is True
    assert task.completed is True
    assert task.mark_complete() is False


def test_pet_add_task_increases_count():
    pet = Pet("Mochi", "dog")
    before = len(pet.tasks)
    task = Task("Walk", "08:00", DAY)
    pet.add_task(task)
    assert len(pet.tasks) == before + 1
    assert pet.tasks[0] is task


def test_owner_collects_every_pets_tasks(system):
    owner, dog, _ = system
    cat = Pet("Luna", "cat")
    owner.add_pet(cat)
    dog_task = Task("Walk", "09:00", DAY)
    cat_task = Task("Meds", "08:00", DAY)
    dog.add_task(dog_task)
    cat.add_task(cat_task)
    assert owner.get_all_tasks() == [(dog, dog_task), (cat, cat_task)]


def test_scheduler_reads_owner_aggregation_method():
    class TrackingOwner(Owner):
        calls = 0

        def get_all_tasks(self):
            self.calls += 1
            return super().get_all_tasks()

    owner = TrackingOwner("Jordan")
    dog, cat = Pet("Mochi", "dog"), Pet("Luna", "cat")
    for pet in [dog, cat]:
        owner.add_pet(pet)
        pet.add_task(Task("Food", "08:00", DAY))
    scheduler = Scheduler(owner)
    assert len(scheduler.filter_tasks()) == 2
    assert owner.calls == 1
    assert len(scheduler.detect_conflicts()) == 1
    assert owner.calls == 2


@pytest.mark.parametrize("frequency,days", [("daily", 1), ("weekly", 7)])
def test_overdue_recurrence_uses_completion_date(system, frequency, days):
    _, pet, scheduler = system
    task = Task("Food", "08:00", DAY - timedelta(days=20), frequency=frequency)
    pet.add_task(task)
    following = scheduler.mark_task_complete(pet, task, completion_date=DAY)
    assert following.due_date == DAY + timedelta(days=days)
    assert following.time == "08:00"


def test_recurrence_defaults_to_today(system):
    _, pet, scheduler = system
    today = date.today()
    task = Task("Food", "08:00", today - timedelta(days=3), frequency="daily")
    pet.add_task(task)
    following = scheduler.mark_task_complete(pet, task)
    assert following.due_date == today + timedelta(days=1)
