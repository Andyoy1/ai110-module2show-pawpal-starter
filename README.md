# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Implementation Summary (Phase 2)

The backend lives in `pawpal_system.py` with four classes:

- `Task` (dataclass): one care task; `mark_complete()` sets `completed` to `True`.
- `Pet` (dataclass): a pet and its tasks; `add_task()` rejects a task whose `pet_name` doesn't match the pet.
- `Owner` (dataclass): an owner and their pets; `add_pet()` rejects blank or duplicate names (case-insensitive, whitespace trimmed); `get_all_tasks()` returns a new list of every pet's tasks.
- `Scheduler`: stores the `Owner`; sorting, filtering, conflict detection, and recurring-task completion (see Smarter Scheduling).

`main.py` is a command-line demo and `tests/test_pawpal.py` holds the pytest tests. `app.py` has not been connected yet.

## 🖥️ Sample Output

From `python main.py` (tasks are added out of order across two pets; the demo then sorts, filters, checks conflicts, and completes a daily task):

```
Today's Schedule for Jordan (2026-10-18)
------------------------------------------------------------------
2026-10-18 07:30 | Mochi  | Morning walk    | high   | pending
2026-10-18 08:00 | Luna   | Feed breakfast  | high   | pending
2026-10-18 08:00 | Luna   | Give medicine   | medium | pending
2026-10-18 18:00 | Mochi  | Brush fur       | low    | pending

Mochi's incomplete tasks
------------------------------------------------------------------
2026-10-18 07:30 | Mochi  | Morning walk    | high   | pending
2026-10-18 18:00 | Mochi  | Brush fur       | low    | pending

Conflict warnings
------------------------------------------------------------------
WARNING: Conflict on 2026-10-18 at 08:00: Luna: Feed breakfast, Luna: Give medicine

Completing a daily task
------------------------------------------------------------------
Completed: Feed breakfast (2026-10-18)
Next occurrence: Feed breakfast on 2026-10-19 at 08:00
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage (requires pytest-cov, not in the current venv):
pytest --cov
```

Sample test output:

```
collected 18 items

tests/test_pawpal.py ..................                                  [100%]

============================= 18 passed in 0.33s ==============================
```

Coverage description (behaviors tested; a line-coverage percentage was not measured because `pytest-cov` is not installed):

- Core models: task completion, adding tasks, `get_all_tasks`, duplicate/blank pet names, wrong-pet tasks.
- Sorting: date/time/priority ordering, no mutation of input, explicitly empty list.
- Filtering: combined pet + `completed=False` + date filters.
- Recurrence: daily and weekly (including month/year rollover), no duplicate on repeated completion, no new task for one-time tasks, rejection of an equal-looking but unowned task.
- Conflicts: across pets and within one pet; completed tasks, different dates, and duration-only overlaps are ignored.

## 📐 Smarter Scheduling

All four methods live on `Scheduler` in `pawpal_system.py`.

| Feature | Method | Notes |
|---------|--------|-------|
| Task sorting | `sort_by_time(tasks=None)` | Returns a new list sorted by due date, `HH:MM` time, then priority (high, medium, low). Defaults to all of the owner's tasks; an explicit empty list returns `[]`. Input is never mutated. |
| Filtering | `filter_tasks(pet_name=None, completed=None, due_date=None)` | Applies every supplied filter together. `completed=False` is a real filter (checked with `is not None`). |
| Conflict handling | `detect_conflicts(tasks=None)` | Groups incomplete tasks by `(due_date, time)` and returns one warning per group with 2+ tasks, naming each pet and description. Works across and within pets. Only exact start-time matches count; duration overlaps are ignored. |
| Recurring tasks | `mark_task_complete(task)` | Verifies the exact task object is owned (identity, not equality) or raises `ValueError`. Already-completed returns `None`. Once-tasks return `None`; daily/weekly tasks add and return a fresh incomplete copy due 1 or 7 days later. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
