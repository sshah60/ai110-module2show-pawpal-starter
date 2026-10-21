"""Exercise actual Streamlit widgets and reruns without needing a browser."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def widget(elements, label):
    return next(item for item in elements if item.label == label)


def click(app, label):
    widget(app.button, label).click().run()
    assert not app.exception


def test_add_edit_schedule_complete_and_session_state():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not app.exception
    widget(app.text_input, "Pet name").set_value("Mochi")
    click(app, "Add pet")
    widget(app.text_input, "Task title").set_value("Breakfast")
    widget(app.selectbox, "Frequency").select("daily")
    click(app, "Add task")
    assert len(app.session_state.owner.pets[0].tasks) == 1
    widget(app.text_input, "Edit title").set_value("Morning food")
    click(app, "Save task changes")
    assert app.session_state.owner.pets[0].tasks[0].title == "Morning food"
    click(app, "Generate schedule")
    assert len(app.table) == 2
    assert "Morning food" in app.table[1].value.to_string()
    click(app, "Mark task complete")
    tasks = app.session_state.owner.pets[0].tasks
    assert len(tasks) == 2
    assert tasks[0].completed and not tasks[1].completed
    assert (tasks[1].due_date - tasks[0].due_date).days == 1
    assert len(app.session_state.owner.pets) == 1
    assert not app.exception


def test_duplicate_pet_and_cross_pet_conflict_warning():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    for name in ["Mochi", "Luna"]:
        widget(app.text_input, "Pet name").set_value(name)
        click(app, "Add pet")
    widget(app.text_input, "Pet name").set_value("Mochi")
    click(app, "Add pet")
    assert any("unique pet name" in item.value for item in app.error)
    widget(app.text_input, "Task title").set_value("Food")
    click(app, "Add task")
    widget(app.selectbox, "Pet").select("Luna")
    widget(app.text_input, "Task title").set_value("Meds")
    click(app, "Add task")
    assert any("conflicts with" in item.value for item in app.warning)
    widget(app.selectbox, "Filter by pet").select("Luna").run()
    assert len(app.table[0].value) == 1
    assert app.table[0].value.iloc[0]["Pet"] == "Luna"
    widget(app.number_input, "Available care minutes").set_value(0)
    click(app, "Generate schedule")
    assert any("No pending task fits" in item.value for item in app.info)
