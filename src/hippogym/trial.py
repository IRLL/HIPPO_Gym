from copy import deepcopy
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from hippogym.event_handler import EventHandler
    from hippogym.trialsteps.trialstep import TrialStep


class Trial:
    """A single experiment instance."""

    def __init__(self, steps: List["TrialStep"]) -> None:
        self.steps = steps
        self.event_handler: Optional["EventHandler"] = None

    def build(self, event_handler: "EventHandler"):
        """Build trial events architecture."""
        self.event_handler = event_handler
        for step in self.steps:
            step.build(event_handler)

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
