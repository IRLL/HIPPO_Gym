"""Test that a built InteractiveStep can recive and send events to multiprocessing queues."""

from multiprocessing import Queue
from hippogym.event_handler import EventHandler
from hippogym.trialsteps.trialstep import InteractiveStep
from hippogym.ui_elements.ui_element import UIElement

import pytest
import pytest_check as check


class DummyInteractiveStep(InteractiveStep):
    def run(self) -> None:
        pass


class DummyUIElement(UIElement):
    def params_dict(self) -> dict:
        return {"name": self.name}


class TestEventArchitecture:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Build a dummy situation."""
        self.in_q = Queue()
        self.out_q = Queue()
        self.event_handler = EventHandler(self.in_q, self.out_q)

        self.uie1 = DummyUIElement("UIE1")
        self.uie2 = DummyUIElement("UIE2")

        self.intstep = DummyInteractiveStep([self.uie1, self.uie2])
        self.intstep.build(self.event_handler)

    def test_UIElements_send(self):
        """Anything sent by a UIElement should go in the output queue."""

        messages_sent = []
        for ui_element in (self.uie1, self.uie2):
            ui_element.send()
            messages_sent.append({ui_element.name: {"name": ui_element.name}})

        messages_recv = []
        while not self.out_q.empty():
            message_recv = self.out_q.get_nowait()
            messages_recv.append(message_recv)

        check.equal(messages_sent, messages_recv)

    def test_UIElements_recv(self):
        """UIElements should recieve messages of topics they are subscribed to."""
        raise NotImplementedError
