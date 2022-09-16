import pytest
import pytest_check as check
from pytest_mock import MockerFixture

from hippogym.ui_elements.ui_element import UIElement


class DummyUIElement(UIElement):
    def __init__(self, *args, **kwargs) -> None:
        self.dummy_attr = kwargs.pop("dummy_attr", None)
        super().__init__(*args, **kwargs)

    def dict(self) -> dict:
        return {"Dummy": {"dummy_attr": self.dummy_attr}}


class TestUIElement:
    """UIElement"""

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        self.message_handler = mocker.MagicMock()
        self.out_q = mocker.MagicMock()

    def test_update_to_value(self):
        """should update attributes to given value"""
        ui_element = DummyUIElement(self.message_handler, self.out_q)
        ui_element.update(dummy_attr=2)
        check.equal(ui_element.dummy_attr, 2)

    def test_update_to_none(self):
        """should update attributes to None if they are given"""
        ui_element = DummyUIElement(self.message_handler, self.out_q, dummy_attr=2)
        check.equal(ui_element.dummy_attr, 2)
        ui_element.update(dummy_attr=None)
        check.is_none(ui_element.dummy_attr)
