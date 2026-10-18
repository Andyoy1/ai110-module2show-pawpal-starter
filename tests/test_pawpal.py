from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def make_task(pet_name="Mochi", description="Walk", time="08:00"):
    return Task(description, pet_name, date(2026, 1, 1), time, 20, "high")


def test_mark_complete_sets_completed():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_to_pet():
    pet = Pet("Mochi", "dog")
    task = make_task()
    pet.add_task(task)
    assert pet.tasks == [task]


def test_get_all_tasks_includes_both_pets():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    walk = make_task("Mochi", "Walk")
    feed = make_task("Luna", "Feed")
    mochi.add_task(walk)
    luna.add_task(feed)

    all_tasks = owner.get_all_tasks()

    assert len(all_tasks) == 2
    assert walk in all_tasks and feed in all_tasks


def test_get_all_tasks_returns_new_list():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    owner.add_pet(mochi)
    mochi.add_task(make_task())

    owner.get_all_tasks().clear()

    assert len(mochi.tasks) == 1


def test_duplicate_pet_name_rejected_case_insensitive():
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog"))
    with pytest.raises(ValueError):
        owner.add_pet(Pet("  mochi ", "cat"))
    assert len(owner.pets) == 1


def test_blank_pet_name_rejected():
    owner = Owner("Jordan")
    with pytest.raises(ValueError):
        owner.add_pet(Pet("   ", "dog"))


def test_task_for_wrong_pet_rejected():
    pet = Pet("Mochi", "dog")
    with pytest.raises(ValueError):
        pet.add_task(make_task(pet_name="Luna"))
    assert pet.tasks == []


# ---- Scheduler (Phase 4) ----

D = date(2026, 1, 1)


def setup():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    return owner, mochi, luna, Scheduler(owner)


def task(pet="Mochi", desc="Walk", time="08:00", priority="high",
         frequency="once", due=D):
    return Task(desc, pet, due, time, 20, priority, frequency)


def test_sort_orders_by_date_time_then_priority_without_mutating():
    owner, mochi, luna, sched = setup()
    low = task("Mochi", "low", "08:00", "low")
    high = task("Luna", "high", "08:00", "high")
    med = task("Mochi", "med", "08:00", "medium")
    early = task("Luna", "early", "07:00", "low")
    later_day = task("Mochi", "next day", "06:00", "high", due=D + timedelta(days=1))
    for t in (low, med, later_day):
        mochi.add_task(t)
    for t in (high, early):
        luna.add_task(t)
    original = owner.get_all_tasks()

    result = sched.sort_by_time()

    assert result == [early, high, med, low, later_day]
    assert owner.get_all_tasks() == original

    supplied = [low, high]
    assert sched.sort_by_time(supplied) == [high, low]
    assert supplied == [low, high]


def test_sort_explicit_empty_list_returns_empty():
    owner, mochi, _, sched = setup()
    mochi.add_task(task())
    assert sched.sort_by_time([]) == []


def test_filter_combined_with_completed_false():
    _, mochi, luna, sched = setup()
    pending = task("Mochi", "pending")
    done = task("Mochi", "done")
    done.mark_complete()
    other_day = task("Mochi", "other day", due=D + timedelta(days=1))
    luna_task = task("Luna", "luna")
    for t in (pending, done, other_day):
        mochi.add_task(t)
    luna.add_task(luna_task)

    assert sched.filter_tasks(pet_name="Mochi", completed=False, due_date=D) == [pending]
    assert sched.filter_tasks(completed=True) == [done]
    assert sched.filter_tasks(pet_name="Luna") == [luna_task]
    assert len(sched.filter_tasks()) == 4


def test_daily_completion_creates_next_day_task():
    _, mochi, _, sched = setup()
    t = task(frequency="daily", due=date(2026, 1, 31))
    mochi.add_task(t)

    new = sched.mark_task_complete(t)

    assert t.completed is True
    assert new is not t and new.completed is False
    assert new.due_date == date(2026, 2, 1)
    assert (new.description, new.pet_name, new.time, new.priority, new.frequency) == (
        t.description, t.pet_name, t.time, t.priority, "daily")
    assert new in mochi.tasks and len(mochi.tasks) == 2


def test_weekly_completion_creates_task_seven_days_later():
    _, mochi, _, sched = setup()
    t = task(frequency="weekly", due=date(2026, 12, 28))
    mochi.add_task(t)

    new = sched.mark_task_complete(t)

    assert new.due_date == date(2027, 1, 4)
    assert new.frequency == "weekly"


def test_repeated_completion_creates_no_duplicate():
    _, mochi, _, sched = setup()
    t = task(frequency="daily")
    mochi.add_task(t)
    sched.mark_task_complete(t)

    assert sched.mark_task_complete(t) is None
    assert len(mochi.tasks) == 2


def test_once_completion_creates_no_new_task():
    _, mochi, _, sched = setup()
    t = task()
    mochi.add_task(t)

    assert sched.mark_task_complete(t) is None
    assert t.completed is True
    assert mochi.tasks == [t]


def test_conflict_across_pets():
    _, mochi, luna, sched = setup()
    mochi.add_task(task("Mochi", "Walk", "08:00"))
    luna.add_task(task("Luna", "Feed", "08:00"))

    warnings = sched.detect_conflicts()

    assert len(warnings) == 1
    for text in ("Mochi", "Walk", "Luna", "Feed", "08:00"):
        assert text in warnings[0]


def test_conflict_within_same_pet():
    _, mochi, _, sched = setup()
    mochi.add_task(task("Mochi", "Walk", "08:00"))
    mochi.add_task(task("Mochi", "Brush", "08:00"))
    assert len(sched.detect_conflicts()) == 1


def test_no_conflict_for_completed_different_date_or_time():
    _, mochi, luna, sched = setup()
    done = task("Mochi", "Done", "08:00")
    done.mark_complete()
    mochi.add_task(done)
    luna.add_task(task("Luna", "Feed", "08:00"))
    mochi.add_task(task("Mochi", "Tomorrow", "08:00", due=D + timedelta(days=1)))
    mochi.add_task(task("Mochi", "Overlap", "08:10"))  # overlaps by duration only

    assert sched.detect_conflicts() == []
    assert sched.detect_conflicts([]) == []


def test_unowned_equal_task_rejected_without_mutation():
    _, mochi, _, sched = setup()
    owned = task(frequency="daily")
    mochi.add_task(owned)
    lookalike = task(frequency="daily")
    assert lookalike == owned

    with pytest.raises(ValueError):
        sched.mark_task_complete(lookalike)

    assert lookalike.completed is False
    assert owned.completed is False
    assert mochi.tasks == [owned]


def test_empty_owner_scheduler_methods_return_empty():
    sched = Scheduler(Owner("Jordan"))
    assert sched.sort_by_time() == []
    assert sched.filter_tasks() == []
    assert sched.filter_tasks(pet_name="Mochi", completed=False) == []
    assert sched.detect_conflicts() == []


def test_pet_with_no_tasks_does_not_break_other_pets():
    owner, mochi, luna, sched = setup()
    feed = task("Luna", "Feed")
    luna.add_task(feed)

    assert sched.filter_tasks(pet_name="Mochi") == []
    assert sched.sort_by_time() == [feed]
    assert sched.detect_conflicts() == []


def test_complete_task_with_no_pets_rejected():
    sched = Scheduler(Owner("Jordan"))
    with pytest.raises(ValueError):
        sched.mark_task_complete(task())
