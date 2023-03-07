import pytest
import pytest_check as check
from pytest_mock import MockerFixture

from hippogym.ui_elements.ui_element import UIElement


class DummyUIElement(UIElement):
    def __init__(self, **kwargs) -> None:
        self.dummy_attr = kwargs.pop("dummy_attr", None)
        super().__init__("Dummy")

    def params_dict(self) -> dict:
        return {"dummy_attr": self.dummy_attr}


class TestUIElement:
    """UIElement"""

    def test_update_to_value(self, mocker: MockerFixture):
        """should update attributes to given value"""
        ui_element = DummyUIElement()
        ui_element.send = mocker.Mock()
        ui_element.update(dummy_attr=2)
        check.equal(ui_element.dummy_attr, 2)

    def test_update_to_none(self, mocker: MockerFixture):
        """should update attributes to None if they are given"""
        ui_element = DummyUIElement(dummy_attr=2)
        ui_element.send = mocker.Mock()
        check.equal(ui_element.dummy_attr, 2)
        ui_element.update(dummy_attr=None)
        check.is_none(ui_element.dummy_attr)
