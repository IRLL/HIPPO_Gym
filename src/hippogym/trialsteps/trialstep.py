from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Union

from hippogym.event_handler import EventHandler

if TYPE_CHECKING:
    from hippogym.ui_elements.ui_element import UIElement


class TrialStep(ABC):
    """Abstract class for single trial step."""

    def __init__(self) -> None:
        self.event_handler: Optional[EventHandler] = None

    def build(self, event_handler: EventHandler) -> None:
        """Build the TrialStep events architecture."""
        self.event_handler = event_handler

    @abstractmethod
    def run(self) -> None:
        """Run the trial step"""


class HtmlStep(TrialStep):
    """A static html page step."""

    def __init__(self, html_content: Union[str, Path]) -> None:
        self.html_content = html_content
        super().__init__()

    def run(self) -> None:
        """Run the html step"""
        raise NotImplementedError


class InteractiveStep(TrialStep):
    """A step where user interacts with hippogym UIElements."""

    def __init__(self, ui_elements: List["UIElement"]) -> None:
        self.ui_elements: List["UIElement"] = ui_elements
        super().__init__()

    def build(self, event_handler: EventHandler) -> None:
        """Initialize multiprocessing queues."""
        super().build(event_handler)
        for ui_element in self.ui_elements:
            ui_element.build(self)
        self.send()

    def send(self) -> None:
        """Send ui_elements to frontend."""
        for ui_element in self.ui_elements:
            ui_element.send()
