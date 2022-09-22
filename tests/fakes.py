from typing import Callable


class FakeProcess:
    def __init__(
        self,
        target: Callable,
        target_args: tuple = None,
        target_kwargs: dict = None,
        *args,
        **kwargs
    ) -> None:
        self.target = target
        self.args = target_args if target_args is not None else tuple()
        self.kwargs = target_kwargs if target_kwargs is not None else {}

    def start(self):
        self.target(*self.args, **self.kwargs)
