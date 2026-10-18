"""Demo script for the PawPal+ backend."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(tasks) -> None:
    for task in tasks:
        status = "done" if task.completed else "pending"
        print(
            f"{task.due_date} {task.time} | {task.pet_name:<6} | "
            f"{task.description:<15} | {task.priority:<6} | {status}"
        )


def main() -> None:
    today = date.today()

    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added deliberately out of time order, across two pets.
    mochi.add_task(Task("Brush fur", "Mochi", today, "18:00", 15, "low", "weekly"))
    luna.add_task(Task("Feed breakfast", "Luna", today, "08:00", 10, "high", "daily"))
    mochi.add_task(Task("Morning walk", "Mochi", today, "07:30", 30, "high"))
    luna.add_task(Task("Give medicine", "Luna", today, "08:00", 5, "medium"))

    scheduler = Scheduler(owner)

    print(f"Today's Schedule for {owner.name} ({today})")
    print("-" * 66)
    print_tasks(scheduler.sort_by_time(scheduler.filter_tasks(due_date=today)))

    print("\nMochi's incomplete tasks")
    print("-" * 66)
    print_tasks(
        scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi", completed=False))
    )

    print("\nConflict warnings")
    print("-" * 66)
    for warning in scheduler.detect_conflicts():
        print(f"WARNING: {warning}")

    print("\nCompleting a daily task")
    print("-" * 66)
    feed = scheduler.filter_tasks(pet_name="Luna", completed=False)[0]
    next_task = scheduler.mark_task_complete(feed)
    print(f"Completed: {feed.description} ({feed.due_date})")
    if next_task:
        print(f"Next occurrence: {next_task.description} on {next_task.due_date} at {next_task.time}")


if __name__ == "__main__":
    main()
