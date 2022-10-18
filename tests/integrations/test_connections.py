import asyncio
import json
from websockets.client import connect

import pytest
import pytest_check as check
from pytest_mock import MockerFixture

from hippogym.hippogym import HippoGym

from tests.fakes import FakeProcess
from tests import server_client_interaction, get_uri


class TestHippoGym:
    """HippoGym"""

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        mocker.patch("hippogym.hippogym.Process", FakeProcess)

        self.trial = mocker.Mock()
        self.trial_config = mocker.Mock()
        self.trial_config.sample = lambda _: self.trial
        self.hippo = HippoGym(self.trial_config)

    def test_trial_run_on_user_connect(
        self, mocker: MockerFixture, unused_tcp_port: int
    ):
        """should start a Trial if a user connects."""

        mocker.patch("hippogym.communicator.EventHandler")
        mocker.patch("hippogym.communicator.WebSocketCommunicator.producer_handler")
        mocker.patch("hippogym.communicator.WebSocketCommunicator.consumer_handler")

        async def fake_user_connect(uri: str, user_id: str):
            """Connect send user_id then close connextion"""
            connexion_msg = json.dumps({"userId": user_id})
            async with connect(uri) as websocket:
                await websocket.send(connexion_msg)
                print(f"{user_id} > {connexion_msg}")
                server_message = await websocket.recv()
                print(f"{user_id} < {server_message}")

        user_id = "fake_user"
        host = "localhost"
        port = unused_tcp_port
        uri = get_uri(host, port)

        asyncio.run(
            server_client_interaction(
                server_coroutine=self.hippo.start_server(host, port),
                client_coroutine=fake_user_connect(uri, user_id),
            )
        )
        check.is_true(self.trial.run.called)
        check.is_not_in(user_id, self.hippo.trials)
