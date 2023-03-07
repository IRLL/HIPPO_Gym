import logging
import time
from typing import Callable


def get_logger(name: str) -> logging.Logger:
    """Get a hippogym logger by the given name.

    Often the name given is the module name : __name__.

    Args:
        name (str): Name of the logger to get.

    Returns:
        logging.Logger: A logger.
    """
    return logging.getLogger(name)


class TimeActor:
    """Perform a function in given time intervals."""

    def __init__(self, func: Callable[[None], None], interval: float) -> None:
        self.start_time = time.time()
        self.last_tick = self.start_time
        self.interval = interval
        self.func = func

    def tick(self):
        """Attempt to perform an action, will only succeed if time interval was long enough."""
        now = time.time()
        delta = now - self.last_tick
        if delta >= self.interval:
            self.last_tick = time.time()
            self.func()
