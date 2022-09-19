import pytest_check as check

from hippogym.ui_elements.building_blocks.button import Button, build_arrow_button


def test_button_to_dict():
    """Button should convert to dict ready for messages"""
    expected_dict = {
        "Button": {
            "image": None,
            "icon": "FaPlayCircle",
            "text": "Start",
            "color": "white",
            "bgcolor": "green",
            "value": "start",
        }
    }
    button = Button(
        icon="FaPlayCircle",
        text="Start",
        color="white",
        bgcolor="green",
        value="start",
    )
    check.equal(button.dict(), expected_dict)


def test_build_arrow_button():
    """build_arrow_button should convert give expected up button."""
    expected_button = Button(
        icon="FaArrowUp",
        text=None,
        color="black",
        bgcolor="white",
        value="up",
    )
    arrow_button = build_arrow_button("up")
    check.equal(arrow_button, expected_button)
