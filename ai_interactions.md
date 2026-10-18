# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

ChatGPT was used to plan staged prompts; Claude Code (an AI agent working in the repo) implemented and tested each stage. Separate implementation, algorithm, and testing chats were used. Prompts below are summaries, not exact quotes. Stages 1 and 2 are described from the git history (`chore: add class skeletons from UML`, `feat: implement core pet care classes and CLI demo`) because those chats are not part of the record available when this log was written; no prompt text or results are claimed for them beyond what the commits show.

**What task did you give the agent?**

| Stage | Summary of the task given |
|-------|---------------------------|
| 1. Design / skeleton planning | Turn the UML (`diagrams/uml.mmd`) into class skeletons with attributes and signatures only (commit `96bfc8c`). |
| 2. Core implementation | Implement `Task`, `Pet`, `Owner` and a CLI demo in `main.py` (commit `d90d754`); connect Streamlit forms to the backend (commit `d77e7e6`). |
| 3. Scheduling algorithms | Implement the four `Scheduler` stubs: `sort_by_time`, `filter_tasks`, `detect_conflicts`, `mark_task_complete`, with detailed rules (date/time/priority ordering, no mutation, explicit empty list, `completed=False`, exact-start-time conflicts, identity-based ownership check, daily/weekly recurrence, no duplicates on repeated completion). Update `main.py` to demo them, add tests, and refresh the README. |
| 4. UI integration | Update `app.py` to use `filter_tasks`, `sort_by_time`, `detect_conflicts` (across all pets for the selected date) and `mark_task_complete` only; add per-task completion buttons with unique keys, a success message that survives the rerun, and keep the existing forms and session state. |
| 5. Testing / debugging | Review backend tests for missing cases (empty owner, pet with no tasks); verify the UI with Streamlit AppTest and save useful tests in `tests/test_app.py`; run the full suite and `main.py`. |
| 6. Final documentation | Update the README (features, commands, demo walkthrough, actual outputs, provisional 4/5 reliability, limitations); create `diagrams/uml_final.mmd` and preserve the original as `uml_draft.mmd`; complete `reflection.md`; check `.gitignore` and untrack generated cache files; fill this log. |

**What did the agent do?**

- **Stage 3:** read `pawpal_system.py`, `main.py`, the tests and README; edited `pawpal_system.py` (added `PRIORITY_ORDER` and `RECURRENCE_DAYS` constants, implemented the four methods); rewrote `main.py`; added 11 backend tests; ran `main.py` and pytest (18 passed); updated the README. `pytest --cov` failed because `pytest-cov` is not installed, so the README describes coverage by behavior and does not give a percentage.
- **Stage 4:** replaced the "All Tasks" section of `app.py` with a Schedule section (date, pet and status filters, conflict warnings, completion buttons).
- **Stage 5:** added 3 backend tests and `tests/test_app.py` (6 AppTest tests). Full suite: 27 passed (21 backend, 6 UI). `main.py` ran cleanly.
- **Stage 6:** README rewrite, UML files, `reflection.md`, and removing the tracked `__pycache__` `.pyc` from the Git index only (local file kept). Nothing was committed or pushed by the agent.

**What did you have to verify or fix manually?**

- Automated checks found and fixed two problems in the agent's first UI tests: the path to `app.py` was resolved relative to `tests/` (fixed with an absolute path), and a test's "Pet" selection matched the add-task form's selectbox instead of the schedule filter (fixed by looking widgets up by key).
- Two README slips were caught and fixed: a mangled Windows venv activation command in the setup instructions and a stale "app.py has not been connected yet" sentence.
- The agent's first attempt at a shell command was rejected during the Phase 4 session, and the work continued afterwards.
- The agent could not check the app in a real browser; the owner's manual browser check of `streamlit run app.py` worked. Still not checked: a line-coverage percentage.
- Human review kept the simple four-class design and exact-time conflicts rather than expanding into duration-overlap scheduling.
