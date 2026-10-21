# PawPal+ design review

## Three core user actions

1. Add a pet to an owner.
2. Schedule a care task for a pet.
3. View today's tasks across all pets.

## Building blocks

| Class | Information | Responsibilities |
|---|---|---|
| Owner | Name, preference notes, pets | Add pets; return all pets' tasks together |
| Pet | Name, species, tasks | Add tasks and keep each pet's list separate |
| Task | Title, time, date, duration, priority, frequency, completion | Validate input; mark itself complete |
| Scheduler | Owner | Read Owner.get_all_tasks(); sort, filter, warn, recur, and build plans |

## Skeleton review

The earlier implementation let Scheduler gather tasks directly. The screenshot explicitly requires an Owner aggregation method, so this revision moves collection into Owner.get_all_tasks(). It returns (pet, task) pairs to keep the pet's name available for display and conflicts.

Task.mark_complete() handles the basic status change; Scheduler.mark_task_complete() manages recurrence. The UI uses the scheduler so recurring tasks create their next instance.

## Algorithm review

A dictionary keyed by (date, time) keeps conflict detection simple. A nested pairwise loop is also understandable but does unnecessary comparisons. Keep explicit filtering loops instead of compressing all conditions into a long comprehension.

## Review order

This revision was reviewed from Phase 1 through Phase 6: design and skeleton, backend/CLI, UI, algorithms, tests, then documentation. The existing implementation was retained as a reference. The phase-one skeleton is saved separately in this folder; it is not imported by the app. Existing history was not rewritten.
