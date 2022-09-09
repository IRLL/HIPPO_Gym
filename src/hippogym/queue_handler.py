def check_queue(queue):
    messages = []
    while not queue.empty():
        messages.append(queue.get(False))
    return messages


def check_queues(queues):
    response = []
    for q in queues:
        messages = check_queue(q)
        if messages:
            for message in messages:
                response.append(message)
    return response
