from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from hippogym.event_handler import POLL_QUEUES, EventsQueues
from hippogym.queue_handler import check_queues, create_or_get_queue

if TYPE_CHECKING:
    from multiprocessing import Queue

    from hippogym.ui_elements.ui_element import UIElement


class TrialStep(ABC):
    """Abstract class for single trial step."""

    def __init__(self) -> None:
        self.queues = {}

    @abstractmethod
    def build(self, queues: Optional[Dict[EventsQueues, "Queue"]] = None) -> None:
        """Build the TrialStep multiprocessing Queues."""
        create_or_get_queue(self.queues, EventsQueues.OUTPUT)

    @abstractmethod
    def start(self) -> None:
        """Initialize the TrialStep."""

    @abstractmethod
    def run(self) -> None:
        """Run the trial step"""


class HtmlStep(TrialStep):
    """A static html page step."""

    def __init__(self, html_content: Union[str, Path]) -> None:
        self.html_content = html_content
        super().__init__()

    def build(self, queues: Optional[Dict[EventsQueues, "Queue"]] = None) -> None:
        """Build multiprocessing queues for html."""
        raise NotImplementedError

    def start(self) -> None:
        """Initialize the TrialStep."""
        raise NotImplementedError

    def run(self) -> None:
        """Run the html step"""
        raise NotImplementedError


class InteractiveStep(TrialStep):
    """A step where user interacts with hippogym UIElements."""

    def __init__(self, ui_elements: List["UIElement"]) -> None:
        self.ui_elements: List["UIElement"] = ui_elements
        super().__init__()

    def build(self, queues: Optional[Dict[EventsQueues, "Queue"]] = None) -> None:
        """Initialize multiprocessing queues."""
        self.queues = queues if queues is not None else {}
        for queue in POLL_QUEUES:
            create_or_get_queue(self.queues, queue)
        for ui_element in self.ui_elements:
            ui_element.build(self)

    def start(self):
        """Start UIElements Threads."""
        for ui_element in self.ui_elements:
            ui_element.start()
        self.send()

    def poll(self) -> List[dict]:
        """Get messages from poll queues (KEYBOARD, BUTTON, STANDARD)."""
        return check_queues([self.queues[queue] for queue in POLL_QUEUES])

    def send(self) -> None:
        """Send ui_elements to frontend."""
        for ui_element in self.ui_elements:
            ui_element.send()
