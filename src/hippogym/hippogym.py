import time

from typing import Dict, Union
from multiprocessing import Process

from hippogym.trial import Trial, TrialConfig, DeterministicTrialConfig
from hippogym.trialsteps.trialstep import TrialStep
from hippogym.log import TimeActor, get_logger

LOGGER = get_logger(__name__)

UserID = str


class HippoGym:
    """Main class for a full HippoGym experiment."""

    def __init__(self, trial_config: Union[TrialConfig, Trial, TrialStep]) -> None:
        """Initialize an HippoGym experiment.

        Args:
            trial_config (TrialConfig | Trial | TrialStep): Configuration to use for Trials.
                If a single Trial or a single TrialStep is given, it will be converted to a
                DeterministicTrialConfig.

        """
        if isinstance(trial_config, TrialStep):
            trial_config = Trial(steps=[trial_config])
        if isinstance(trial_config, Trial):
            trial_config = DeterministicTrialConfig(trial_config)
        self.trial_config = trial_config

        self.trials: Dict[UserID, Process] = {}
        self._trial_seed = 0  # TODO use yield

    def start_trial(self, user_id: UserID):
        """Start a trial for the given user.

        Args:
            user_id (UserID): Unique ID for the user.

        Raises:
            ValueError: If user is already in trial.
        """
        trial = self.trial_config.sample(self._trial_seed)
        new_trial_process = Process(target=trial.run)
        if user_id in self.trials:
            raise ValueError(f"{user_id=} already in trial")
        self.trials[user_id] = new_trial_process
        self._trial_seed += 1
        new_trial_process.start()

    def stop_trial(self, user_id: UserID):
        """Stop the trial for the given user.

        Args:
            user_id (UserID): Unique ID of the user.
        """
        trial_process = self.trials.pop(user_id)
        trial_process.terminate()

    def standby(self) -> None:
        """Wait until a connection is done by a user."""

        def _log_standby():
            LOGGER.debug("HippoGym in standby")

        standby_printer = TimeActor(_log_standby, 2)
        while True:
            time.sleep(0.01)
            if not self.trials:
                standby_printer.tick()
