from multiprocessing import Queue
from typing import Dict, List

from hippogym.event_handler import EventsQueues


def check_queue(queue: Queue) -> List[Dict[str, str]]:
    messages = []
    while not queue.empty():
        messages.append(queue.get_nowait())
    return messages


def check_queues(queues: List[Queue]) -> List[Dict[str, str]]:
    response = []
    for queue in queues:
        response += check_queue(queue)
    return response


def create_or_get_queue(
    queues: Dict[EventsQueues, Queue],
    queue_type: EventsQueues,
) -> Queue:
    """Utilitary function to get the relevant queue from the dict of queues

    If absent, it will create the relevant Queue.

    """

    if queue_type not in queues:
        queues[queue_type] = Queue()
    return queues[queue_type]
