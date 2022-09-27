from copy import deepcopy
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from multiprocessing import Queue

    from hippogym.event_handler import EventsQueues
    from hippogym.trialsteps import TrialStep


class Trial:
    """A single experiment instance."""

    def __init__(self, steps: List["TrialStep"]) -> None:
        self.steps = steps
        self.queues: Dict["EventsQueues", "Queue"] = {}

    def build(self):
        """Build multiprocessing queues for every step."""
        for step in self.steps:
            step.build(self.queues)

    def run(self):
        """Run the Trial step by step."""
        for step in self.steps:
            step.start()
            step.run()


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
        if len(self.steps) == 1:
            return self.steps[0]
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
