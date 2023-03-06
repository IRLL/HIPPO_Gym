from typing import List
import json

import pytest_check as check
import asyncio

from hippogym import HippoGym

from tests import server_client_interaction, get_uri
from websockets.client import connect


def check_ui_elements(
    hippo: HippoGym,
    expected_ui_elements: List[str],
    port: int,
    host="localhost",
):
    async def fake_user_connect(uri: str, user_id: str):
        """Connect send user_id then close connextion"""
        async with connect(uri) as websocket:
            # Connects
            await websocket.send(json.dumps({"userId": user_id}))
            message = await websocket.recv()

            ui_elements_messages = [message]
            assert user_id in hippo.trials, "Trial did not start."

            for _ in expected_ui_elements[1:]:
                ui_elements_messages.append(await websocket.recv())

            for expected_ui_element in expected_ui_elements:
                check.is_true(
                    any(expected_ui_element in msg for msg in ui_elements_messages),
                    f"Expected UIElement was not found: {expected_ui_element}",
                )

    user_id = "fake_user"
    uri = get_uri(host, port)
    asyncio.run(
        server_client_interaction(
            server_coroutine=hippo.start_server(host, port),
            client_coroutine=fake_user_connect(uri, user_id),
        )
    )
    hippo.stop_trial(user_id)
