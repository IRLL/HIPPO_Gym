from multiprocessing import Queue
from typing import Dict, List


def check_queue(queue: Queue) -> List[Dict[str, str]]:
    messages = []
    while not queue.empty():
        messages.append(queue.get_nowait())
    return messages


def check_queues(queues: Dict[str, Queue]) -> List[str]:
    response = []
    for queue in queues:
        messages = check_queue(queue)
        if messages:
            response += messages
    return response
