"""Test that EventHandler behave as expected."""

from hippogym.event_handler import EventHandler
from multiprocessing import Queue

import pytest_check as check
from pytest_mock import MockerFixture


def test_events_dispatch(mocker: MockerFixture):
    event_handler = EventHandler(Queue(), Queue())
    event_handler.dispatch = mocker.MagicMock()

    expected_calls_args = [
        ("ui.KeyboardEvent", "a", 0),
        ("ui.KeyboardEvent", "b", 1),
    ]

    message_content = {"a": 0, "b": 1}
    event_handler.emit({"KeyboardEvent": message_content})

    calls_done = [call.args for call in event_handler.dispatch.call_args_list]

    for call_args in expected_calls_args:
        check.is_in(call_args, calls_done)
