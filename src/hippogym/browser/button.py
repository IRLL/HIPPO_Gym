from dataclasses import asdict, dataclass, field
from enum import Enum


@dataclass
class Button:
    """Button for the control panel."""

    icon: str
    text: str
    color: str
    bgcolor: str
    value: str
    image: str = field(default=None)

    def dict(self) -> dict:
        """Convert Button to a dict."""
        return {"Button": asdict(self)}


class Direction(Enum):
    """Classic cross directions"""

    UP: str = "up"
    DOWN: str = "down"
    LEFT: str = "left"
    RIGHT: str = "right"


def build_arrow_button(direction: Direction):
    """Build an arrow button in the given direction."""
    if not isinstance(direction, Direction):
        direction = Direction(direction)

    return Button(
        icon=f"FaArrow{direction.value.capitalize()}",
        text=None,
        color="black",
        bgcolor="white",
        value=direction.value,
    )


start_button = Button(
    icon="FaPlayCircle",
    text="Start",
    color="white",
    bgcolor="green",
    value="start",
)
reset_button = Button(
    icon="FaRedo",
    text="Reset",
    color="white",
    bgcolor="red",
    value="reset",
)
submit_button = Button(
    icon="FaCheckCircle",
    text="Submit",
    color="white",
    bgcolor="green",
    value="submit",
)

end_button = Button(
    image=None,
    icon="FaStopCircle",
    text="End",
    color="white",
    bgcolor="blue",
    value="end",
)

pause_button = Button(
    image=None,
    icon="FaPauseCircle",
    text="Pause",
    color="white",
    bgcolor="orange",
    value="pause",
)

good_button = Button(
    image=None,
    icon="FaCheck",
    text="Good",
    color="white",
    bgcolor="green",
    value="good",
)

bad_button = Button(
    image=None,
    icon="FaTimes",
    text="Bad",
    color="white",
    bgcolor="red",
    value="bad",
)

up_button = build_arrow_button(Direction.UP)
down_button = build_arrow_button(Direction.DOWN)
left_button = build_arrow_button(Direction.LEFT)
right_button = build_arrow_button(Direction.RIGHT)


standard_controls = [
    start_button,
    reset_button,
    end_button,
    left_button,
    right_button,
    up_button,
    down_button,
]
