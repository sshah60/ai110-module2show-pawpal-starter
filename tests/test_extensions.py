from datetime import date, timedelta
import json
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler

DAY = date(2026, 10, 21)


def setup_owner():
    owner = Owner("Jordan", "Morning care")
    for name in ["Mochi", "Luna"]:
        owner.add_pet(Pet(name, "other"))
    return owner


def test_json_round_trip(tmp_path):
    owner = setup_owner()
    owner.pets[0].add_task(Task("Food", "08:00", DAY, frequency="daily", completed=True))
    owner.pets[1].add_task(Task("Vet", "09:00", DAY, 30, "high", "weekly"))
    path = tmp_path / "data.json"
    owner.save_to_json(path)
    loaded = Owner.load_from_json(path)
    assert loaded is not owner
    assert loaded.name == owner.name and loaded.preferences == owner.preferences
    assert len(loaded.pets) == 2
    assert loaded.pets[0].tasks[0].completed is True
    assert loaded.pets[1].tasks[0].task_id == owner.pets[1].tasks[0].task_id
    assert loaded.pets[1].tasks[0].due_date == DAY
    assert loaded.pets[1].tasks[0].frequency == "weekly"
    assert len(Scheduler(loaded).filter_tasks(completed=False)) == 1
    loaded.save_to_json(path)
    assert not path.with_suffix('.json.tmp').exists()


@pytest.mark.parametrize("content", ['not json', '{}', '{"name":"Jordan","pets":[{}]}'])
def test_bad_json_is_not_overwritten(tmp_path, content):
    path = tmp_path / "data.json"
    path.write_text(content)
    with pytest.raises(ValueError):
        Owner.load_from_json(path)
    assert path.read_text() == content


def test_priority_before_time_across_pets():
    owner = setup_owner()
    owner.pets[0].add_task(Task("Play", "07:00", DAY, priority="low"))
    owner.pets[1].add_task(Task("Meds", "09:00", DAY, priority="high"))
    owner.pets[0].add_task(Task("Food", "08:00", DAY, priority="high"))
    assert [task.title for _, task in Scheduler(owner).sort_by_priority()] == ["Food", "Meds", "Play"]


def test_free_slot_uses_durations_across_pets():
    owner = setup_owner()
    owner.pets[0].add_task(Task("Walk", "08:00", DAY, 30))
    owner.pets[1].add_task(Task("Meds", "08:20", DAY, 20))
    owner.pets[1].add_task(Task("Brush", "09:00", DAY, 30))
    scheduler = Scheduler(owner)
    assert scheduler.next_available_slot(DAY, 20) == "08:40"
    assert scheduler.next_available_slot(DAY, 21) == "09:30"


def test_free_slot_empty_done_and_day_boundary():
    owner = setup_owner()
    scheduler = Scheduler(owner)
    assert scheduler.next_available_slot(DAY, 10) == "08:00"
    assert scheduler.next_available_slot(DAY, 30, "23:30") == "23:30"
    assert scheduler.next_available_slot(DAY, 31, "23:30") is None
    owner.pets[0].add_task(Task("Old", "08:00", DAY, 60, completed=True))
    assert scheduler.next_available_slot(DAY, 20) == "08:00"
    owner.pets[1].add_task(Task("Overnight", "23:50", DAY - timedelta(days=1), 30))
    assert scheduler.next_available_slot(DAY, 10, "00:00") == "00:20"


def test_free_slot_invalid_input():
    scheduler = Scheduler(setup_owner())
    with pytest.raises(ValueError):
        scheduler.next_available_slot(DAY, 0)
    with pytest.raises(ValueError):
        scheduler.next_available_slot(DAY, 20, "25:00")
