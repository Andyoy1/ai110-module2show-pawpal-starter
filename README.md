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

## Features

- Add pets (unique names, case-insensitive) and care tasks with date, time, duration, priority, and frequency (once/daily/weekly).
- Schedule view for a chosen date (defaults to today; future dates allowed), filterable by pet and status.
- Tasks are sorted by date and time, with higher priority first when times match.
- Conflict warnings for incomplete tasks that start at exactly the same time, across all pets, regardless of the display filters. Tasks are never moved.
- One-click completion; daily and weekly tasks automatically create the next occurrence.
- Input validation for blank descriptions and missing times.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Commands

```bash
python main.py            # CLI demo
streamlit run app.py      # Streamlit UI
python -m pytest          # all tests (backend + Streamlit AppTest UI tests)
```

## Design (UML)

- [diagrams/uml_draft.mmd](diagrams/uml_draft.mmd): the original design.
- [diagrams/uml_final.mmd](diagrams/uml_final.mmd): the final design matching `pawpal_system.py` (also copied to [diagrams/uml.mmd](diagrams/uml.mmd), the file the starter expects).

## Implementation Summary (Phase 2)

The backend lives in `pawpal_system.py` with four classes:

- `Task` (dataclass): one care task; `mark_complete()` sets `completed` to `True`.
- `Pet` (dataclass): a pet and its tasks; `add_task()` rejects a task whose `pet_name` doesn't match the pet.
- `Owner` (dataclass): an owner and their pets; `add_pet()` rejects blank or duplicate names (case-insensitive, whitespace trimmed); `get_all_tasks()` returns a new list of every pet's tasks.
- `Scheduler`: stores the `Owner`; sorting, filtering, conflict detection, and recurring-task completion (see Smarter Scheduling).

`main.py` is a command-line demo and `tests/test_pawpal.py` holds the pytest tests. `app.py` is the Streamlit UI and `tests/test_app.py` holds its AppTest tests.

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
python -m pytest
```

Actual output:

```
collected 27 items

tests	est_app.py ......                                                 [ 22%]
tests	est_pawpal.py .....................                               [100%]

============================= 27 passed in 11.86s =============================
```

Coverage (behaviors tested; no line-coverage percentage, since `pytest-cov` is not installed):

- **Backend (`tests/test_pawpal.py`, 21 tests):** task completion, adding tasks, `get_all_tasks`, duplicate/blank pet names, wrong-pet tasks; sorting (date/time/priority, no mutation, explicit empty list); combined filters with `completed=False`; daily/weekly recurrence including month/year rollover; no duplicate on repeated completion; once-tasks create nothing; unowned look-alike task rejected; conflicts across and within pets, ignoring completed tasks, other dates, and duration-only overlaps; empty owner, pet with no tasks, and completing a task with no pets.
- **UI (`tests/test_app.py`, 6 Streamlit AppTest tests):** two pets and tasks survive interactions; chronological display; pet/status/date filters; cross-pet same-time warning (still shown when filtered); completing a daily task keeps the completed original, creates exactly one incomplete next-day task, keeps the success message after rerun, and shows it on the next day; blank-description and missing-time validation.

### Reliability: 4/5 stars (provisional)

My confidence is fairly high because the scheduling logic and the main UI workflow are covered by 27 passing tests, and a manual check of the app in the browser (`streamlit run app.py`) worked. The rating is provisional: it is my own judgement, not a measured result. Not checked: line-coverage numbers, and many-task or many-user scale.

### Limitations

- **Session-only storage:** data lives in Streamlit session state and is lost on refresh or restart.
- **Exact-start-time conflicts:** only identical start times warn; overlapping durations (08:00 for 30 min vs. 08:10) do not.
- **Recurrence from the original due date:** the next occurrence is the original due date plus 1 or 7 days, not the completion date, so completing a task late can create an occurrence already in the past.

## 📐 Smarter Scheduling

All four methods live on `Scheduler` in `pawpal_system.py`.

| Feature | Method | Notes |
|---------|--------|-------|
| Task sorting | `sort_by_time(tasks=None)` | Returns a new list sorted by due date, `HH:MM` time, then priority (high, medium, low). Defaults to all of the owner's tasks; an explicit empty list returns `[]`. Input is never mutated. |
| Filtering | `filter_tasks(pet_name=None, completed=None, due_date=None)` | Applies every supplied filter together. `completed=False` is a real filter (checked with `is not None`). |
| Conflict handling | `detect_conflicts(tasks=None)` | Groups incomplete tasks by `(due_date, time)` and returns one warning per group with 2+ tasks, naming each pet and description. Works across and within pets. Only exact start-time matches count; duration overlaps are ignored. |
| Recurring tasks | `mark_task_complete(task)` | Verifies the exact task object is owned (identity, not equality) or raises `ValueError`. Already-completed returns `None`. Once-tasks return `None`; daily/weekly tasks add and return a fresh incomplete copy due 1 or 7 days later. |

## 📸 Demo Walkthrough

A concrete workflow in the Streamlit app (`streamlit run app.py`):

1. Add two pets: **Mochi** (dog) and **Luna** (cat).
2. Add tasks for today: Mochi "Evening walk" at 18:00 (low), Luna "Feed breakfast" at 08:00 (high, daily), Mochi "Morning walk" at 07:30 (high). Leaving the description blank or the time empty shows an error instead.
3. In **Schedule**, the table lists 07:30, 08:00, 18:00 in time order, even though they were added out of order.
4. Add Mochi "Give bath" at 08:00. A warning appears: *Scheduling conflict (all pets, ...)* naming Luna's feeding and Mochi's bath. Choosing Pet = Mochi still shows the warning, because conflicts check all pets.
5. Click **Complete: 08:00 Luna - Feed breakfast**. The row shows Done, and a success message gives the next due date (tomorrow).
6. Change **Date** to tomorrow to see the new incomplete "Feed breakfast" occurrence.

