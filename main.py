"""Demo script for the PawPal+ backend."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    today = date.today()

    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", "Mochi", today, "07:30", 30, "high"))
    luna.add_task(Task("Feed breakfast", "Luna", today, "08:00", 10, "high", "daily"))
    mochi.add_task(Task("Brush fur", "Mochi", today, "18:00", 15, "low", "weekly"))

    scheduler = Scheduler(owner)

    print(f"Today's Schedule for {scheduler.owner.name} ({today})")
    print("-" * 60)
    for task in scheduler.owner.get_all_tasks():
        status = "done" if task.completed else "pending"
        print(
            f"{task.time} | {task.pet_name:<6} | {task.description:<15} "
            f"| {task.priority:<6} | {status}"
        )


if __name__ == "__main__":
    main()
