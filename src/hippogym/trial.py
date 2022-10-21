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
        self.event_handler: Optional["EventHandler"] = None

    def build(self, in_q: Queue, out_q: Queue):
        """Build trial events architecture."""
        self.event_handler = EventHandler(in_q, out_q)
        for step in self.steps:
            step.build(self.event_handler)

    def run(self):
        """Run the Trial step by step."""
        for step in self.steps:
            step.start()
            step.run()

    def build_and_run(self, in_q: Queue, out_q: Queue):
        """Build then run the Trial step by step."""
        self.build(in_q, out_q)
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
