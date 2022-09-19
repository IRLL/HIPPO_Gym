import pytest
import pytest_check as check
from pytest_mock import MockerFixture

from hippogym.ui_elements.ui_element import UIElement


class DummyUIElement(UIElement):
    def __init__(self, message_handler, **kwargs) -> None:
        self.dummy_attr = kwargs.pop("dummy_attr", None)
        super().__init__("Dummy", message_handler)

    def params_dict(self) -> dict:
        return {"dummy_attr": self.dummy_attr}


class TestUIElement:
    """UIElement"""

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        self.message_handler = mocker.MagicMock()

    def test_update_to_value(self):
        """should update attributes to given value"""
        ui_element = DummyUIElement(self.message_handler)
        ui_element.update(dummy_attr=2)
        check.equal(ui_element.dummy_attr, 2)

    def test_update_to_none(self):
        """should update attributes to None if they are given"""
        ui_element = DummyUIElement(self.message_handler, dummy_attr=2)
        check.equal(ui_element.dummy_attr, 2)
        ui_element.update(dummy_attr=None)
        check.is_none(ui_element.dummy_attr)
