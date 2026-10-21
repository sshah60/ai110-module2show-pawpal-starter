"""Deterministic multi-pet demonstration: python main.py."""
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    day = date(2026, 10, 21)
    owner = Owner("Jordan", "Keep morning care short")
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Evening walk", "18:00", day, 30, "low"))
    mochi.add_task(Task("Breakfast", "08:00", day, 10, "high", "daily"))
    luna.add_task(Task("Medication", "08:00", day, 5, "high", "daily"))
    luna.add_task(Task("Brush coat", "09:00", day, 15, "medium", "weekly"))
    scheduler = Scheduler(owner)
    print(f"Today's Schedule for {owner.name}: {day} (30 minute budget)")
    chosen, skipped = scheduler.build_schedule(day, 30)
    for pet, task, reason in chosen:
        print(f"{task.time} | {pet.name} | {task.title} | {reason}")
    for pet, task in skipped:
        print(f"Skipped: {pet.name} / {task.title} (does not fit remaining budget)")
    for warning in scheduler.detect_conflicts():
        print(f"WARNING: {warning}")
    print(f"Owner combined task count: {len(owner.get_all_tasks())}")
    print("Mochi tasks (chronological):")
    for pet, task in scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi")):
        print(f"  {task.time} {task.title}")
    next_task = scheduler.mark_task_complete(mochi, mochi.tasks[1])
    print(f"Completed Breakfast; next daily occurrence: {next_task.due_date} {next_task.time}")
    print(f"Completed tasks: {len(scheduler.filter_tasks(completed=True))}")


if __name__ == "__main__":
    main()
