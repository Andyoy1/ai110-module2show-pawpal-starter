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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
