# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial design uses four classes. `Task` (a dataclass) holds one care task: its description, pet name, due date, time, duration, priority, frequency, and completed flag, plus `mark_complete()`. `Pet` (a dataclass) holds a name, species, and its own list of tasks, with `add_task()`. `Owner` (a dataclass) holds the owner's name and list of pets, with `add_pet()` and `get_all_tasks()`; pet names are unique within an owner. `Scheduler` holds an `Owner` and does the "thinking": it gets tasks through `Owner.get_all_tasks()` so it works across multiple pets, then sorts them by date and time (priority breaks ties), filters them by pet, completion, or date, warns about incomplete tasks that share a date and time, and completes tasks (creating the next occurrence for daily/weekly ones). Owner owns Pets, Pet owns Tasks, and Scheduler uses the Owner. I kept the data classes simple and put all the scheduling behavior in one place.

Three core user actions the design supports:

1. **Add multiple pets:** the owner adds pets (name and species) to their profile.
2. **Schedule care tasks:** the owner adds tasks to a pet with a date, time, duration, priority, and frequency.
3. **View and manage a daily schedule:** the owner sees tasks sorted by time, filters them, sees conflict warnings, and marks tasks complete.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The initial architecture stayed largely intact: the same four classes and relationships survived (compare `diagrams/uml_draft.mmd` with `diagrams/uml_final.mmd`). Implementation only refined details:

- `mark_task_complete()` now returns `Optional[Task]` instead of `Task`, because one-time tasks and already-completed tasks create nothing.
- It checks that the exact task object belongs to the owner (object identity, not equality), so an equal-looking task from somewhere else is rejected with a `ValueError` and nothing is changed.
- `Pet.add_task()` and `Owner.add_pet()` validate their input (wrong-pet tasks, blank or duplicate pet names).
- In the UI, conflict warnings look at all pets on the selected date, even when the display is filtered to one pet.

These were refinements, not a redesign.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler orders tasks by due date and time first, because a daily plan is mainly about *when* things happen. Priority only breaks ties when two tasks start at the same time (high before medium before low). It also filters by pet, completion status, and date, and warns about incomplete tasks that start at the same date and time, whether they belong to different pets or the same pet. Completed tasks and tasks on different dates never conflict.


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Tradeoff:** conflicts are exact-start-time matches only, and they warn instead of moving tasks. A 30-minute task at 08:00 and another at 08:10 overlap in real life but are not flagged. I think this is reasonable for a small personal planner: the rule is easy to explain, easy to test, and leaves the owner in control of the schedule. Detecting duration overlaps would need a more complicated algorithm and decisions about what to do with them.

**Related recurrence choices:** completing a daily or weekly task keeps the completed original as history and creates a new incomplete task from the *original* due date plus 1 or 7 days. Repeated completion of the same task creates nothing extra, so no duplicates appear. A downside is that completing a task late can create an occurrence that is already in the past.


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

ChatGPT helped plan staged prompts for the project. Claude implemented the code and tests. I used separate implementation, algorithm, and testing chats so each task had a focused context. The most helpful prompts were specific ones that listed exact behaviors, such as sort order, how `completed=False` should filter, what counts as a conflict, and what must not be mutated, and asked for tests for each.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The AI initially suggested keeping only `diagrams/uml.mmd` to avoid duplication. During review with ChatGPT, we corrected that approach because the assignment explicitly requires `uml_draft.mmd` and `uml_final.mmd`, so both required files were included (and `uml.mmd` was updated to match the final diagram).

For verification, Claude ran the CLI demo (`python main.py`) and the automated tests, and 27 tests passed. That checking also caught two real problems that were then fixed: the UI tests first failed because the path to `app.py` was resolved from the wrong folder, and one test's "Pet" selection was ambiguous because the add-task form and the schedule filter both had a widget with that label.


---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The suite passes 27 tests: 21 backend and 6 UI.

- **Backend:** sorting (date, time, priority tie-breaks, no mutation of input, explicit empty list), combined filters including `completed=False`, daily and weekly recurrence with date rollover, no duplicate on repeated completion, no new task for one-time tasks, rejection of an unowned equal-looking task, conflicts across and within pets, and empty-owner and no-task-pet cases.
- **UI (Streamlit AppTest):** pets and tasks surviving interactions, chronological display, pet/status/date filters, a same-time warning across pets, completing a daily task creating exactly one next-day occurrence, and blank-description and missing-time validation.

These matter because scheduling bugs are easy to miss by eye, especially duplicates and wrong filters.


**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

My provisional confidence is 4/5. Streamlit AppTest verified the UI interactions, and my manual check of the app in the browser worked. Next I would test larger schedules, duration overlaps if that feature were added, and late completion of recurring tasks (an occurrence created in the past).


---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the separation of classes: `Task`, `Pet`, and `Owner` hold the data, and `Scheduler` holds the scheduling logic. I am also satisfied that the tests cover both layers: the backend tests exercise the scheduling logic, and the UI tests exercise the Streamlit interface.


**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Possible improvements: persistent storage (data currently lives only in the Streamlit session), duration-overlap conflict detection, and testing larger schedules.


**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Specific, staged prompts, and checking the actual results after each stage, helped keep the project organized. The design stayed simple because each stage had a clear scope, such as the four-class design and exact-start-time conflicts.

