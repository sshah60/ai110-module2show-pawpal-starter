# Assignment requirements review

Reviewed against all 17 screenshots supplied directly in this chat. They cover the overview and phases 1–6, ending at the optional extensions heading.

| Phase | Required result | Evidence |
|---|---|---|
| 1 | Three core user actions and class responsibilities | reflection.md 1a; docs/design.md |
| 1 | Mermaid draft with four classes and relationships | diagrams/uml_draft.mmd |
| 1 | Dataclass skeleton and relationship review | docs/phase1_skeleton.py; docs/design.md |
| 2 | Task, Pet, Owner, Scheduler implementation | pawpal_system.py |
| 2 | Owner method combines every pet's tasks; Scheduler uses it | Owner.get_all_tasks(); Scheduler.filter_tasks(); explicit tests |
| 2 | CLI: owner, two pets, at least three tasks, readable schedule | main.py; cli_output.txt; README Sample Output |
| 2 | Completion and task-addition tests | tests/test_pawpal.py |
| 2 | Method docstrings and implementation summary | pawpal_system.py; README System design |
| 3 | Imports, session state, pet/task/schedule actions | app.py; tests/test_app.py |
| 4 | Sorting, pet/status filters, daily/weekly recurrence | Scheduler methods; CLI; tests |
| 4 | Conflict warning across same/different pets | detect_conflicts(); CLI; app.py; tests |
| 4 | Algorithm review and tradeoff explanation | docs/design.md; reflection.md 2b |
| 4 | Smarter Scheduling documentation names methods | README Smarter Scheduling |
| 5 | Core behavior test plan, empty cases, duplicate times | docs/test_plan.md; tests/ |
| 5 | Successful real pytest output and confidence rating | test_output.txt; README Testing PawPal+ |
| 6 | UI displays sorted/filtered tasks and warnings | app.py; Streamlit AppTest |
| 6 | Final Mermaid source matches implementation | diagrams/uml_final.mmd; diagrams/uml.mmd |
| 6 | Features, text walkthrough, real CLI sample | README.md |
| 6 | Structured reflection and AI strategy answers | reflection.md |

## Short checkpoint answers

- **How should Scheduler get pet data?** Call Owner.get_all_tasks(), which returns pet-task pairs across all pets.
- **Which method adds a pet?** Owner.add_pet(). Session state retains the owner, and the rerun shows the updated list.
- **How should a conflict appear?** Use st.warning() with the date, time, pet names, and tasks, then offer editing to fix the time.
- **How can sorting stay readable?** Use sorted() with a date/time key and leave the original list unchanged.
- **How does recurrence work?** timedelta(days=1) or timedelta(days=7) advances the completion date while preserving the scheduled time.

## Workflow notes

This was a correction of an existing AI-assisted implementation, not a rewritten development history. The design and skeleton were reviewed before backend corrections. Separate phase chats were not created. Local commits record actual changes; remote push remains pending user confirmation. Optional extensions were not required or claimed, apart from documenting the agent workflow.
