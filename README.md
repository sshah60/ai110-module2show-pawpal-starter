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
- Keep data during UI reruns and save/load pets and tasks between app runs.
- Suggest the next free time slot across all pets, accounting for durations.

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
| Recurrence | `Scheduler.mark_task_complete()` | Create one new task at completion date + 1 or 7 days; repeated completion does not duplicate it |
| Free slot | `Scheduler.next_available_slot()` | Earliest duration-aware gap across all pets before midnight |
| Priority order | `Scheduler.sort_by_priority()` | High, medium, low first; date/time breaks ties |
| Persistence | `Owner.save_to_json()`, `Owner.load_from_json()` | Save and reconstruct pets/tasks with ISO dates |
| Editing | `Scheduler.update_task()` | Validate before replacing the task, preserving its ID |

## Demo Walkthrough

1. Save the owner name and optional preference notes.
2. Add Mochi (dog) and Luna (cat).
3. Add a high-priority daily Breakfast task for Mochi at 08:00, lasting 10 minutes. Add a Luna task at the same date and time to see a conflict warning.
4. Open **Edit or complete a task** to change a pending task or mark it complete. Completing a daily task creates tomorrow's instance; weekly creates one seven days later.
5. Under **Build Schedule**, choose the date, pet/status filters, and available care minutes. Click **Generate schedule** to see the priority-based plan and why each task fits.
6. Lower the budget to see tasks skipped. The plan always uses pending tasks, even when the table displays completed tasks.
7. Open **Find the next available slot**, enter a date, duration, and earliest time, then click **Find free slot**. The suggestion avoids occupied durations across all pets.
8. Open **Saved data** and click **Save data**. Pets, tasks, dates, IDs, and completion status load automatically when the app starts again.

### Sample Output

Actual output from `python main.py`:

```text
Today's Schedule for Jordan: 2026-10-21 (30 minute budget)
08:00 | Mochi | Breakfast | high priority; 10 min fits the budget
08:00 | Luna | Medication | high priority; 5 min fits the budget
09:00 | Luna | Brush coat | medium priority; 15 min fits the budget
Skipped: Mochi / Early play (does not fit remaining budget)
Skipped: Mochi / Evening walk (does not fit remaining budget)
WARNING: 2026-10-21 08:00: Mochi: Breakfast conflicts with Luna: Medication.
Owner combined task count: 5
Mochi tasks (chronological):
  07:00 Early play
  08:00 Breakfast
  18:00 Evening walk

PRIORITY QUEUE (priority first, then time)
PRIORITY   TIME   PET      TASK
------------------------------------------------
HIGH       08:00  Mochi    Breakfast
HIGH       08:00  Luna     Medication
MEDIUM     09:00  Luna     Brush coat
LOW        07:00  Mochi    Early play
LOW        18:00  Mochi    Evening walk
Next free 20-minute slot after 08:00: 08:10
JSON round trip: 2 pets, 5 tasks restored
Completed Breakfast; next daily occurrence: 2026-10-22 08:00
Completed tasks: 1
```

## Testing PawPal+

```bash
python -m pytest
```

The 36 cases check task completion, task addition, Owner aggregation, scheduler use of that method, chronological sorting, empty schedules, combined filters, budgets and priorities, same-pet and cross-pet conflicts, daily/weekly date rollover, repeated completion, invalid input, safe editing, and duplicate guards. Streamlit AppTest also executes real widget interactions for adding, editing, completing, filtering, and generating a plan.

Actual successful output from the VS Code project folder:

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/shrey/Desktop/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 36 items

tests/test_app.py ...                                                    [  8%]
tests/test_extensions.py ........                                        [ 30%]
tests/test_pawpal.py .........................                           [100%]

============================== 36 passed in 2.90s ==============================
```

Confidence level: **4/5** for this prototype. Tests verify the implemented rules; they do not prove every possible use case.

## Limits and decisions

- Click **Save data** after edits. Unsaved changes remain session-only. All local sessions share the saved data.json file; concurrent saves use last-writer-wins.
- Conflicts check identical start times, not overlapping durations. Warnings do not move or reject tasks.
- The budget is total care minutes, not a continuous availability window. Requested times remain fixed.
- Selection is greedy by priority, not an optimal packing algorithm.
- Preferences are stored as notes and are not interpreted automatically.
- Recurrence advances from the completion date: daily is tomorrow, weekly is seven days later.
- One owner per session; no accounts, time zones, or database.
- Free-slot search uses stored pending occurrences only. Future recurring instances are created on completion, not expanded automatically through a search horizon.

## Optional extensions

### 1. Next available slot

`Scheduler.next_available_slot(day, duration_minutes, earliest)` sorts pending intervals across all pets and moves a candidate start past occupied intervals until a gap fits. It considers durations, overlaps, and overnight tasks. It returns `None` when no slot fits before midnight. It suggests a slot without changing existing tasks.

### 2. Data persistence

`Owner.save_to_json()` converts the nested dataclasses to dictionaries, stores dates as ISO strings, writes a temporary file, then replaces `data.json`. `Owner.load_from_json()` rebuilds and validates the owner, pets, and tasks. No extra serialization library is needed.

The app loads saved data automatically. Click **Save data** after changes; unsaved changes are not restored. Keep `data.json` beside `app.py`. It is ignored by Git so personal pet records are not committed. The CLI demonstrates save/load using a temporary file so it does not overwrite app data.

### 3. Priority scheduling

`Scheduler.sort_by_priority()` returns high, medium, then low priorities, using date/time to break ties. `build_schedule()` uses this order to select tasks within the budget, then displays the chosen daily plan chronologically. The **PRIORITY QUEUE** in the CLI sample demonstrates priority before time across two pets.

### 4. Output formatting

The app uses `st.metric()` for pet/pending/completed totals, status symbols (✅ Complete and 🕒 Pending), `st.success()` for saved/finished actions, and `st.warning()` for conflicts. `st.table()` presents schedules; the CLI uses fixed-width columns for its priority queue. No additional formatting library is required.

### 5. Prompt comparison

`ai_interactions.md` compares the implemented interval sweep with a user-supplied Claude response. Claude's example was executed successfully. The log records useful ideas, limitations, verification, and the decision to retain validated same-day results. Exact model versions were not provided.

Modified files: `pawpal_system.py`, `app.py`, `main.py`, `tests/test_app.py`, `tests/test_extensions.py`, both final UML sources, `.gitignore`, `README.md`, `reflection.md`, and `ai_interactions.md`.

## Project guide

See [design notes](docs/design.md), [requirements checklist](docs/requirements_checklist.md), [test plan](docs/test_plan.md), and `reflection.md`.
