"""Test that EventHandler behave as expected."""

from hippogym.event_handler import EventHandler
from multiprocessing import Queue
from pytest_mock import MockerFixture


def test_events_dispatch(mocker: MockerFixture):
    event_handler = EventHandler(Queue(), Queue())
    event_handler.emitter = mocker.MagicMock()

    message_content = {"a": 0, "b": 1}
    event_handler.emit({"KeyboardEvent": message_content})
    event_handler.emitter.emit.assert_called_with("ui.KeyboardEvent", message_content)
