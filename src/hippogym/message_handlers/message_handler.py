import time
from threading import Thread
from typing import TYPE_CHECKING, Any, Callable, Optional

from hippogym.event_handler import EventsQueues
from hippogym.queue_handler import check_queue, create_or_get_queue

if TYPE_CHECKING:
    from hippogym.trial import Trial


class MessageHandler(Thread):
    """Handle messages between a UIElement and the client."""

    def __init__(
        self,
        in_queue_type: EventsQueues,
        out_queue_type: EventsQueues = EventsQueues.OUTPUT,
    ) -> None:
        """Handle messages between a UIElement and the client.

        Args:
            in_queue_type (EventsQueues): Incomming queue for events.
                Must be an element of EventsQueues.
            out_queue_type (EventsQueues, optional): Output queue for events.
                Defaults to EventsQueues.OUTPUT.
        """
        Thread.__init__(self, daemon=True)
        self.trial: Optional["Trial"] = None
        self.in_queue_type = in_queue_type
        self.out_queue_type = out_queue_type
        self.in_queue = None
        self.out_queue = None
        self.handlers = {}

    def set_trial(self, trial: "Trial") -> None:
        """Associate the MessageHandler to a Trial instance."""
        self.trial = trial
        self.in_queue = create_or_get_queue(self.trial.queues, self.in_queue_type)
        self.out_queue = create_or_get_queue(self.trial.queues, self.out_queue_type)

    def send(self, message: Any):
        """Send a message to the output queue."""
        self.out_queue.put_nowait(message)

    def recv_all(self) -> list:
        """Recieve all messages in the incomming queue.

        Returns:
            list: List of found messages.
        """
        if self.in_queue is None:
            return []
        return check_queue(self.in_queue)

    def run(self) -> None:
        """Run the message handler on a new Thread."""
        while True:
            for message in self.recv_all():
                self.call_handlers(message)
            time.sleep(0.01)

    def call_handlers(self, message: dict):
        """Call handlers relevant the incomming message.

        Args:
            message (Any): Incomming message.

        Raises:
            NotImplementedError: If the incomming messag is not a dict.
        """
        if not isinstance(message, dict):
            raise NotImplementedError("Non-dict messages are not supported.")
        for key in message.keys():
            if key in self.handlers:
                handler: Callable[[Optional[str]], None] = self.handlers[key]
                handler(message[key])
