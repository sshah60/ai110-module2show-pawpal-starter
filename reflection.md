# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions are adding a pet, scheduling a care task, and viewing today's tasks. Owner manages pets and combines their tasks; Pet stores details and tasks; Task tracks an activity; Scheduler organizes care.

**b. Design changes**

The full screenshot review moved task collection into Owner.get_all_tasks(), which Scheduler now calls. Task.mark_complete() handles status; the scheduler handles recurrence from the completion date. The design skeleton was revisited before these corrections.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers date, completion status, priority, and available care minutes. It chooses high-priority tasks first, then displays chosen tasks chronologically. Owner preferences are notes only.

**b. Tradeoffs**

Conflicts mean identical start dates and times, not overlapping durations. This keeps the logic simple but can miss partial overlaps. The greedy budget rule is easy to explain but does not guarantee the best possible combination.

## 3. AI Collaboration

**a. How you used AI**

Codex's file editing, test execution, and debugging were most useful. The full screenshot review clarified the multi-pet architecture. Separate phase chats were not used; phase notes and separate files kept the work organized.

**b. Judgment and verification**

The initial AI implementation collected tasks inside Scheduler; this was changed to the required Owner aggregation method. App tests also caught a copied-object issue, fixed with stable selections. These were agent corrections during review.

## 4. Testing and Verification

**a. What you tested**

The 27 tests cover completion, task addition, Owner aggregation, sorting, filtering, budgets, conflicts, recurrence, validation, and app actions. They verify both the core rules and the UI connection.

**b. Confidence**

Confidence: 4/5 for this in-memory prototype, based on the successful run recorded in README. Next tests would cover duration overlaps, time zones, and long-term storage.

## 5. Reflection

**a. What went well**

The CLI and UI share one scheduling layer, so both use the same rules.

**b. What you would improve**

Add persistent storage and duration-aware conflicts. Make owner preferences structured so the scheduler can apply them.

**c. Key takeaway**

The lead architect must define the rules and verify behavior. AI-generated code still needs tests; a success message alone does not prove data was saved.
