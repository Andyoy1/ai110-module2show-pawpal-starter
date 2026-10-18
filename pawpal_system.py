"""PawPal+ backend class skeletons (Phase 1: attributes and signatures only)."""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


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
        pass


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str  # unique within an owner
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        pass


@dataclass
class Owner:
    """A pet owner who has one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner (pet names must be unique)."""
        pass

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        pass


class Scheduler:
    """Organizes an owner's tasks across all of their pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner."""
        pass

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by date and time, using priority to break ties."""
        pass

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        due_date: Optional[date] = None,
    ) -> List[Task]:
        """Return tasks matching the given pet, completion status, and date."""
        pass

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Return warnings for incomplete tasks sharing the same date and time."""
        pass

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task; if recurring, add and return the next occurrence."""
        pass
