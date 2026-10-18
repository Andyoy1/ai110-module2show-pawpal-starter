"""PawPal+ backend class skeletons (Phase 1: attributes and signatures only)."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import List, Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


@dataclass
class Task:
    """A single pet care task."""

    description: str
    pet_name: str
    due_date: date
    time: str  # zero-padded "HH:MM", e.g. "08:30"
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    frequency: str = "once"  # "once", "daily", or "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str  # unique within an owner
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet (the task must be for this pet)."""
        if task.pet_name != self.name:
            raise ValueError(
                f"Task is for '{task.pet_name}', not '{self.name}'."
            )
        self.tasks.append(task)


@dataclass
class Owner:
    """A pet owner who has one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner (pet names must be unique)."""
        new_name = pet.name.strip().lower()
        if not new_name:
            raise ValueError("Pet name cannot be blank.")
        for existing in self.pets:
            if existing.name.strip().lower() == new_name:
                raise ValueError(f"Owner already has a pet named '{pet.name}'.")
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    """Organizes an owner's tasks across all of their pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner."""
        self.owner = owner

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by date and time, using priority to break ties."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(
            tasks,
            key=lambda t: (
                t.due_date,
                t.time,
                PRIORITY_ORDER.get(t.priority, len(PRIORITY_ORDER)),
            ),
        )

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        due_date: Optional[date] = None,
    ) -> List[Task]:
        """Return tasks matching the given pet, completion status, and date."""
        matches = []
        for task in self.owner.get_all_tasks():
            if pet_name is not None and task.pet_name != pet_name:
                continue
            if completed is not None and task.completed != completed:
                continue
            if due_date is not None and task.due_date != due_date:
                continue
            matches.append(task)
        return matches

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Return warnings for incomplete tasks sharing the same date and time."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        groups = {}
        for task in tasks:
            if not task.completed:
                groups.setdefault((task.due_date, task.time), []).append(task)

        warnings = []
        for (due, time), group in sorted(groups.items()):
            if len(group) > 1:
                details = ", ".join(f"{t.pet_name}: {t.description}" for t in group)
                warnings.append(f"Conflict on {due} at {time}: {details}")
        return warnings

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task; if recurring, add and return the next occurrence."""
        # Identity, not equality: an equal-looking Task must not match.
        owning_pet = next(
            (p for p in self.owner.pets if any(t is task for t in p.tasks)), None
        )
        if owning_pet is None:
            raise ValueError("Task does not belong to this owner.")
        if task.completed:
            return None

        task.mark_complete()
        days = RECURRENCE_DAYS.get(task.frequency)
        if days is None:
            return None
        next_task = replace(
            task, due_date=task.due_date + timedelta(days=days), completed=False
        )
        owning_pet.add_task(next_task)
        return next_task
