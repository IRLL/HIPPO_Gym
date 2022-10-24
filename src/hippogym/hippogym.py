import asyncio
from multiprocessing import Process, Queue
from typing import Dict, Optional, Tuple, Union

from websockets.server import WebSocketServerProtocol

from hippogym.communicator import SSLCertificate, WebSocketCommunicator
from hippogym.trial import DeterministicTrialConfig, Trial, TrialConfig
from hippogym.trialsteps.trialstep import TrialStep
from hippogym.log import get_logger

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

    def start(
        self,
        host: str = "localhost",
        port: int = 5000,
        ssl_certificate: Optional["SSLCertificate"] = None,
    ) -> None:
        asyncio.run(self.start_server(host, port, ssl_certificate))

    async def start_server(
        self,
        host: str,
        port: int,
        ssl_certificate: Optional[SSLCertificate] = None,
    ) -> None:
        """Start hippogym server side.

        Args:
            ssl_certificate (Optional[SSLCertificate]): SSL certificate for ssl server.
            host (str): Host for non-ssl server.
            port (int): Port for ssl server, non-ssl server will be on port + 1.
        """
        communicator = WebSocketCommunicator(self, host, port, ssl_certificate)
        await communicator.start()

    async def start_connexion(
        self, websocket: WebSocketServerProtocol, _path: str
    ) -> None:
        """Handle a new websocket connexion.

        Args:
            websocket (WebSocketServerProtocol): Websocket just created.
        """
        user_message: Dict[str, str] = await websocket.recv()
        user_id = user_message.get("userId")
        if user_id is None:
            raise RuntimeError("User connected without anouncing userId first.")
        LOGGER.info("User connected: %s", user_id)
        try:
            self.start_trial(user_id)
        finally:
            self.stop_trial(user_id)

    def start_trial(self, user_id: UserID) -> Tuple[Queue, Queue]:
        """Start a trial for the given user.

        Args:
            user_id (UserID): Unique ID for the user.

        Return:
            Trial: Trial being ran in a new process.

        Raises:
            ValueError: If user is already in trial.
        """
        trial = self.trial_config.sample(self._trial_seed)
        in_q, out_q = Queue(), Queue()

        if user_id in self.trials:
            raise ValueError(f"{user_id=} already in trial")

        new_trial_process = Process(
            name="Trial",
            target=trial.build_and_run,
            args=(in_q, out_q),
        )

        self.trials[user_id] = new_trial_process
        self._trial_seed += 1
        new_trial_process.start()
        return in_q, out_q

    def stop_trial(self, user_id: UserID) -> None:
        """Stop the trial for the given user.

        Args:
            user_id (UserID): Unique ID of the user.
        """
        trial_process = self.trials.pop(user_id)
        trial_process.kill()
        trial_process.join()
        trial_process.close()
