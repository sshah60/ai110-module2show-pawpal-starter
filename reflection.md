# PawPal+ Project Reflection

This reflection describes the AI-assisted work in this project. Personal learning claims are left for the student to verify.

## 1. System Design

**a. Initial design**

The baseline design uses Owner, Pet, Task, and Scheduler. Owners register pets, pets store tasks, and the scheduler selects and orders care.

**b. Design changes**

The final design adds validated edits, stable task IDs, conflict warnings, and recurrence. The draft diagram records the baseline design for comparison; it was saved during final documentation rather than before coding.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers date, completion status, priority, and available care minutes. It chooses high-priority tasks first, then displays chosen tasks chronologically. Owner preferences are notes only.

**b. Tradeoffs**

Conflicts mean identical start dates and times, not overlapping durations. This keeps the logic simple but can miss partial overlaps. The greedy budget rule is easy to explain but does not guarantee the best possible combination.

## 3. AI Collaboration

**a. How you used AI**

Codex inspected the starter, implemented the classes and UI, wrote tests, and ran the CLI and app checks. The request to keep beginner-friendly code and real test output guided the work. Separate phase chats were not used; phases stayed organized through separate files and checks.

**b. Judgment and verification**

The first UI version stored selected Pet objects directly in widgets. App tests showed that tasks could be added to a detached copy. The implementation was revised to select pet names and task IDs, then look up the current objects. This was an agent correction, not a claimed student rejection.

## 4. Testing and Verification

**a. What you tested**

Tests cover sorting, combined filters, budgets, empty schedules, validation, editing, conflicts, and daily/weekly recurrence. App tests cover forms, session persistence, completion, filters, and warnings.

**b. Confidence**

Confidence: 4/5 for this in-memory prototype, based on the successful run recorded in README. Next tests would cover duration overlaps, time zones, and long-term storage.

## 5. Reflection

**a. What went well**

The CLI and UI share one scheduling layer, so both use the same rules.

**b. What you would improve**

Add persistent storage and duration-aware conflicts. Make owner preferences structured so the scheduler can apply them.

**c. Key takeaway**

The lead architect must define the rules and verify behavior. AI-generated code still needs tests; a success message alone does not prove data was saved.
