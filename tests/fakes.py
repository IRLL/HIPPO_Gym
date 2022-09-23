from typing import Callable


class FakeProcess:
    def __init__(
        self,
        target: Callable,
        args: tuple = None,
        kwargs: dict = None,
        *other_args,
        **other_kwargs
    ) -> None:
        self.target = target
        self.target_obj = None
        self.args = args if args is not None else tuple()
        self.kwargs = kwargs if kwargs is not None else {}

    def start(self):
        self.target_obj = self.target(*self.args, **self.kwargs)

    def close(self):
        pass
