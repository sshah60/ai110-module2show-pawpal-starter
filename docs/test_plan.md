# Test plan

1. **Core objects:** add a task, mark it complete, collect all pets' tasks, and confirm Scheduler calls Owner.get_all_tasks().
2. **Ordering and filtering:** use out-of-order times, different dates, multiple pets, and mixed completion states; check combined filters and empty results.
3. **Recurrence:** check daily/weekly rollover, new IDs, preserved time, once-only tasks, and repeated completion without duplicates.
4. **Conflicts and constraints:** check same/different pets at one time, different dates, completed tasks, exact budgets, zero budgets, and invalid input.
5. **UI integration:** add pets/tasks, edit, complete, generate plans, keep session state, filter, and show conflict/empty-budget feedback.

The tests use arrange, act, assert: create a known situation, call the behavior, then compare the actual result with the expected result. AppTest runs Streamlit widget actions and checks both displayed output and stored objects.
