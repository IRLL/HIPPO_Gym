def check_queue(queue):
    message = None
    if not queue.empty():
        message = queue.get(False)
    return message


def check_queues(queues):
    response = []
    for q in queues:
        message = check_queue(queues[q])
        if message:
            response.append(message)
    return response
