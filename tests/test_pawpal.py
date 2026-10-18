from datetime import date

import pytest

from pawpal_system import Owner, Pet, Task


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
