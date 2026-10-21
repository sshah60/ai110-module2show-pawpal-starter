# PawPal+ (Module 2 Project)

PawPal+ helps one owner plan care for multiple pets. It is a small, in-memory Python and Streamlit project based on the CodePath starter.

## Getting started

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
python -m streamlit run app.py
```

## Features

- Register an owner and multiple pets.
- Add and edit tasks with dates, times, durations, priorities, and frequency.
- Filter by pet, date, and completion status; display chronological tasks.
- Select daily care within a minute budget, with reasons and skipped-task explanations.
- Warn about identical start times across pets.
- Complete tasks and create the next daily or weekly occurrence.
- Keep data in Streamlit session state during UI reruns.

## System design

`pawpal_system.py` contains Owner, Pet, Task, and Scheduler. Owner.get_all_tasks() combines tasks across pets; Scheduler reads that method to organize care. Task.mark_complete() changes status, while Scheduler.mark_task_complete() also creates recurrence. `main.py` demonstrates the backend; `app.py` provides the UI. Tests are in `tests/`.

Mermaid sources: [baseline draft](diagrams/uml_draft.mmd), [final UML](diagrams/uml_final.mmd). The starter's `diagrams/uml.mmd` also contains the final diagram. The full screenshot review revisited the design and [class skeleton](docs/phase1_skeleton.py) before correcting the backend. [Design notes](docs/design.md) summarize the four classes and core actions.

## Smarter Scheduling

| Feature | Method | Behavior |
|---|---|---|
| Multi-pet retrieval | `Owner.get_all_tasks()` | Return tasks from all pets; used by Scheduler filtering and scheduling |
| Completion | `Task.mark_complete()` | Set status; scheduler completion adds recurrence |
| Sorting | `Scheduler.sort_by_time()` | New list ordered by date, then time |
| Filtering | `Scheduler.filter_tasks()` | Combine pet, status, and date filters |
| Budget and priorities | `Scheduler.build_schedule()` | High, medium, then low priority; choose tasks that fit remaining minutes; display by time |
| Conflicts | `Scheduler.detect_conflicts()` | Warning strings for pending tasks with identical date/time, including different pets |
| Recurrence | `Scheduler.mark_task_complete()` | Create one new task at scheduled date + 1 or 7 days; repeated completion does not duplicate it |
| Editing | `Scheduler.update_task()` | Validate before replacing the task, preserving its ID |

## Demo Walkthrough

1. Save the owner name and optional preference notes.
2. Add Mochi (dog) and Luna (cat).
3. Add a high-priority daily Breakfast task for Mochi at 08:00, lasting 10 minutes. Add a Luna task at the same date and time to see a conflict warning.
4. Open **Edit or complete a task** to change a pending task or mark it complete. Completing a daily task creates tomorrow's instance; weekly creates one seven days later.
5. Under **Build Schedule**, choose the date, pet/status filters, and available care minutes. Click **Generate schedule** to see the priority-based plan and why each task fits.
6. Lower the budget to see tasks skipped. The plan always uses pending tasks, even when the table displays completed tasks.

### Sample Output

Actual output from `python main.py`:

```text
Today's Schedule for Jordan: 2026-10-21 (30 minute budget)
08:00 | Mochi | Breakfast | high priority; 10 min fits the budget
08:00 | Luna | Medication | high priority; 5 min fits the budget
09:00 | Luna | Brush coat | medium priority; 15 min fits the budget
Skipped: Mochi / Evening walk (does not fit remaining budget)
WARNING: 2026-10-21 08:00: Mochi: Breakfast conflicts with Luna: Medication.
Owner combined task count: 4
Mochi tasks (chronological):
  08:00 Breakfast
  18:00 Evening walk
Completed Breakfast; next daily occurrence: 2026-10-22 08:00
Completed tasks: 1
```

## Testing PawPal+

```bash
python -m pytest
```

The 24 cases check task completion, task addition, Owner aggregation, scheduler use of that method, chronological sorting, empty schedules, combined filters, budgets and priorities, same-pet and cross-pet conflicts, daily/weekly date rollover, repeated completion, invalid input, safe editing, and duplicate guards. Streamlit AppTest also executes real widget interactions for adding, editing, completing, filtering, and generating a plan.

Actual successful output from the VS Code project folder:

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/shrey/Desktop/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 24 items

tests/test_app.py ..                                                     [  8%]
tests/test_pawpal.py ......................                              [100%]

============================== 24 passed in 2.01s ==============================
```

Confidence level: **4/5** for this prototype. Tests verify the implemented rules; they do not prove every possible use case.

## Limits and decisions

- Data is session-only; a new browser session or server restart can lose it.
- Conflicts check identical start times, not overlapping durations. Warnings do not move or reject tasks.
- The budget is total care minutes, not a continuous availability window. Requested times remain fixed.
- Selection is greedy by priority, not an optimal packing algorithm.
- Preferences are stored as notes and are not interpreted automatically.
- Recurrence advances from the scheduled due date. Completing an overdue task may create another overdue instance.
- One owner per session; no accounts, time zones, or database.

## Assignment coverage and AI use

The starter structure and reflection headings are retained. All 17 screenshots attached in this chat were reviewed across phases 1–6. The corrected requirements are mapped in [the checklist](docs/requirements_checklist.md). No separate phase chat history or GitHub submission is claimed. See `reflection.md` and `ai_interactions.md` for short notes.
