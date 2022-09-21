""" HippoGym: A framework for human-in-the-loop experiments. """

import time
from logging import getLogger
from multiprocessing import Process, Queue
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple

from hippogym.bucketer import bucketer
from hippogym.communicator import Communicator
from hippogym.event_handler import EventsQueues
from hippogym.message_handlers.user import UserMessageHandler
from hippogym.queue_handler import check_queues, create_or_get_queue

if TYPE_CHECKING:
    from hippogym.recorder.recorder import Recorder
    from hippogym.ui_elements import UIElement

LOGGER = getLogger(__name__)

POLL_QUEUES = (EventsQueues.KEYBOARD, EventsQueues.BUTTON, EventsQueues.STANDARD)


class HippoGym:
    def __init__(
        self,
        ui_elements: List["UIElement"],
        recorders: Optional[List["Recorder"]] = None,
    ) -> None:

        self.recorders = recorders if recorders is not None else []

        self.user_id: Optional[str] = None
        self.project_id: Optional[str] = None
        self.run = False
        self.stop = False

        # Setup UIElements and their messages queues
        self.ui_elements: List["UIElement"] = []
        self.queues = {}
        for queue in POLL_QUEUES:
            create_or_get_queue(self.queues, queue)
        for ui_element in ui_elements:
            self.add_ui_element(ui_element)
            ui_element.message_handler.start()

        # Setup handler for user connect / disconnect
        self.user_hander = UserMessageHandler()
        self.user_hander.set_queues(self.queues)
        self.user_hander.set_hippo(self)
        self.user_hander.start()

        # Setup Communicator for all messages events on a child process
        self.communicator = Process(
            target=Communicator,
            args=(self.queues,),
            kwargs={
                "address": "localhost",
                "port": 5000,
                "use_ssl": True,
                "force_ssl": False,
                "fullchain_path": "fullchain.pem",
                "privkey_path": "privkey.pem",
            },
            daemon=True,
        )
        self.communicator.start()

    def start_trial(self, user_id: str):
        LOGGER.info("Trial started by user: %s", user_id)
        self.user_id = user_id

    def stop_trial(self, user_id: str):
        LOGGER.info("Trial ended by user: %s", user_id)
        self.user_id = None

    def start(self) -> None:
        self.stop = False
        self.run = True

    def pause(self) -> None:
        self.run = False

    def end(self) -> None:
        self.run = False
        self.stop = True

    def group(self, num_groups: int) -> int:
        if self.user_id is None:
            raise TypeError("User must not be None in order to get user group.")
        return bucketer(self.user_id, num_groups)

    def poll(self) -> List[str]:
        return check_queues([self.queues[queue] for queue in POLL_QUEUES])

    def send(self) -> None:
        print(self.ui_elements)
        for ui_element in self.ui_elements:
            ui_element.send()

    def standby(self) -> None:
        def _log_standby():
            LOGGER.debug("HippoGym in standby")

        time_printer = TimeActor(lambda: _log_standby(), 2)
        while self.user_id is None:
            time.sleep(0.01)
            time_printer.tick()

    def add_ui_element(self, ui_element: "UIElement"):
        self.ui_elements.append(ui_element)
        ui_element.set_queues(self.queues)
        ui_element.set_hippo(self)


class TimeActor:
    def __init__(self, func: Callable[[None], None], interval: float) -> None:
        self.start_time = time.time()
        self.last_tick = self.start_time
        self.interval = interval
        self.func = func

    def tick(self):
        now = time.time()
        delta = now - self.last_tick
        if delta >= self.interval:
            self.last_tick = time.time()
            self.func()
