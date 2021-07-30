def check_queue(queue):
    message = None
    if not queue.empty():
        message = queue.get(False)
    return message


def check_all_queues(queues):
    response = []
    for q in queues:
        message = check_queue(q)
        if message:
            response.append(message)
    return response
