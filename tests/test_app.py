"""Streamlit AppTest checks for the PawPal+ UI."""

from datetime import date, timedelta
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")
TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)


def new_app():
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    return at


def add_pet(at, name, species="dog"):
    at.text_input[1].set_value(name)
    at.selectbox[0].set_value(species)
    next(b for b in at.button if b.label == "Add pet").click()
    at.run()


def add_task(at, pet, description, time, due=TODAY, priority="high", frequency="once"):
    at.selectbox[1].set_value(pet)
    at.text_input[2].set_value(description)
    at.date_input[0].set_value(due)
    if time is not None:
        at.time_input[0].set_value(time)
    at.selectbox[2].set_value(priority)
    at.selectbox[3].set_value(frequency)
    next(b for b in at.button if b.label == "Add task").click()
    at.run()


def schedule_times(at):
    """Time column of the schedule table (last table on the page)."""
    return [row["Time"] for row in at.table[-1].value.to_dict("records")]


def schedule_rows(at):
    return at.table[-1].value.to_dict("records")


def two_pet_app():
    from datetime import time

    at = new_app()
    add_pet(at, "Mochi", "dog")
    add_pet(at, "Luna", "cat")
    add_task(at, "Mochi", "Evening walk", time(18, 0), priority="low")
    add_task(at, "Luna", "Feed breakfast", time(8, 0), frequency="daily")
    add_task(at, "Mochi", "Morning walk", time(7, 30))
    return at


def select(at, label, value):
    """Set a schedule filter (looked up by key; the add-task form also has 'Pet')."""
    key = {"Pet": "pet_filter", "Status": "status_filter"}[label]
    at.selectbox(key=key).set_value(value).run()


def test_pets_and_tasks_survive_interactions():
    at = two_pet_app()
    owner = at.session_state["owner"]
    assert [p.name for p in owner.pets] == ["Mochi", "Luna"]
    assert len(owner.get_all_tasks()) == 3
    select(at, "Status", "Incomplete")
    assert len(owner.get_all_tasks()) == 3
    assert not at.exception


def test_schedule_is_chronological():
    at = two_pet_app()
    assert schedule_times(at) == ["07:30", "08:00", "18:00"]


def test_pet_status_and_date_filters():
    from datetime import time

    at = two_pet_app()
    add_task(at, "Luna", "Vet visit", time(9, 0), due=TOMORROW)

    select(at, "Pet", "Luna")
    assert [r["Description"] for r in schedule_rows(at)] == ["Feed breakfast"]

    select(at, "Pet", "All pets")
    at.date_input(key="view_date").set_value(TOMORROW).run()
    assert [r["Description"] for r in schedule_rows(at)] == ["Vet visit"]

    at.date_input(key="view_date").set_value(TODAY).run()
    owner = at.session_state["owner"]
    next(t for t in owner.get_all_tasks() if t.description == "Morning walk").mark_complete()
    select(at, "Status", "Completed")
    assert [r["Description"] for r in schedule_rows(at)] == ["Morning walk"]
    select(at, "Status", "Incomplete")
    assert [r["Description"] for r in schedule_rows(at)] == ["Feed breakfast", "Evening walk"]


def test_same_time_across_pets_warns_even_when_filtered():
    from datetime import time

    at = two_pet_app()
    assert not at.warning
    add_task(at, "Mochi", "Give bath", time(8, 0), priority="medium")

    assert len(at.warning) == 1
    assert "Feed breakfast" in at.warning[0].value and "Give bath" in at.warning[0].value
    assert "all pets" in at.warning[0].value

    select(at, "Pet", "Mochi")  # filter hides Luna's task but conflict stays
    assert len(at.warning) == 1


def test_completing_daily_task_creates_one_next_day_occurrence():
    at = two_pet_app()
    next(b for b in at.button if "Feed breakfast" in b.label).click()
    at.run()

    owner = at.session_state["owner"]
    feeds = [t for t in owner.get_all_tasks() if t.description == "Feed breakfast"]
    assert len(feeds) == 2
    original = next(t for t in feeds if t.due_date == TODAY)
    new = next(t for t in feeds if t.due_date == TOMORROW)
    assert original.completed is True and new.completed is False

    assert any(str(TOMORROW) in s.value for s in at.success)  # survives rerun
    assert not any("Feed breakfast" in b.label for b in at.button)

    at.date_input(key="view_date").set_value(TOMORROW).run()
    assert [r["Description"] for r in schedule_rows(at)] == ["Feed breakfast"]


def test_validation_blank_description_and_missing_time():
    from datetime import time

    at = new_app()
    add_pet(at, "Mochi")
    add_task(at, "Mochi", "   ", time(8, 0))
    assert any("description" in e.value for e in at.error)

    add_task(at, "Mochi", "Walk", None)
    assert any("time" in e.value for e in at.error)
    assert at.session_state["owner"].get_all_tasks() == []
