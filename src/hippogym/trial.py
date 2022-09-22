from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from hippogym.trialsteps import TrialStep


class Trial:
    """A single experiment instance."""

    def __init__(self, steps: List["TrialStep"]) -> None:
        self.steps = steps
        self.queues = {}

    def run(self):
        """Run the Trial step by step."""
        for step in self.steps:
            step.run()


class TrialConfig:
    """Configuration to generate independant Trial instances."""

    def __init__(self, steps: List["TrialStep"]) -> None:
        self.steps = steps

    def sample(self, seed: int) -> Trial:
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
        self.trial = trial
        super().__init__(self.trial.steps)

    def sample(self, seed: int) -> Trial:
        return self.trial.new()
