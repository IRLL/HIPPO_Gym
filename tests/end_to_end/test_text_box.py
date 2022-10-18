import json

import pytest
import pytest_check as check

from examples.text_box import build_experiment
from websockets.client import connect
import asyncio

from tests.end_to_end import server_client_interaction


def test_text_box(unused_tcp_port: int):
    user_id = "fake_user"
    host = "localhost"
    port = unused_tcp_port
    uri = f"ws://{host}:{port}"

    hippo = build_experiment()

    async def fake_user_connect(uri: str, user_id: str):
        """Connect send user_id then close connextion"""
        async with connect(uri) as websocket:
            # Connects
            await websocket.send(json.dumps({"userId": user_id}))

            message = await websocket.recv()
            ui_elements_messages = [message]
            assert user_id in hippo.trials, "Trial did not start."
            expected_ui_elements = (
                "InfoPanel",
                "TextBox",
                "ControlPanel",
                "GameWindow",
            )

            for _ in expected_ui_elements[1:]:
                ui_elements_messages.append(await websocket.recv())

            for expected_ui_element in expected_ui_elements:
                check.is_true(
                    any(expected_ui_element in msg for msg in ui_elements_messages)
                )

    asyncio.run(
        server_client_interaction(
            server_coroutine=hippo.start_server(host, port),
            client_coroutine=fake_user_connect(uri, user_id),
        )
    )
