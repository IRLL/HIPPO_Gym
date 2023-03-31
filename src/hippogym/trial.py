from copy import deepcopy
from multiprocessing import Queue
from typing import TYPE_CHECKING, List, Optional

from hippogym.event_handler import EventHandler

if TYPE_CHECKING:
    from hippogym.trialsteps.trialstep import TrialStep


class Trial:
    """A single experiment instance."""

    def __init__(self, steps: List["TrialStep"]) -> None:
        self.steps = steps
        self.in_q: Optional[Queue] = None
        self.out_q: Optional[Queue] = None

    def build(self, user_id: str, in_q: Queue, out_q: Queue):
        """Build trial events architecture."""
        self.user_id = user_id
        self.in_q = in_q
        self.out_q = out_q

    def run(self):
        """Run the Trial step by step."""
        for step in self.steps:
            event_handler = EventHandler(self.in_q, self.out_q)
            step.build(self.user_id, event_handler)
            step.run()

    def build_and_run(self, user_id: str, in_q: Queue, out_q: Queue):
        """Build then run the Trial step by step."""
        self.build(user_id, in_q, out_q)
        self.run()


class TrialConfig:
    """Configuration to generate independant Trial instances."""

    def __init__(self, steps: List["TrialStep"]) -> None:
        self.steps = steps

    def sample(self, _seed: Optional[int] = None) -> Trial:
        """Sample a new Trial from a given seed.

        Args:
            seed (int): Seed to ensure Trial reproductibility.

        Returns:
            Trial: A new independant Trial.
        """
        raise NotImplementedError


class DeterministicTrialConfig(TrialConfig):
    """Generate deterministic independant Trial instances."""

    def __init__(self, trial: Trial) -> None:
        """Generate deterministic independant Trial instances.

        Args:
            trial (Trial): Trial to use as a model for generation.
        """
        self.trial_model = deepcopy(trial)

    def sample(self, _seed: Optional[int] = None) -> Trial:
        return deepcopy(self.trial_model)
