import pytest
import pytest_check as check

from hippogym.ui_elements.building_blocks.slider import Slider


class TestSlider:
    """Slider"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.slider = Slider(
            title="SliderTitle",
            icon="IconStrValue",
            min_value=0,
            max_value=1000,
            init_value=100,
        )

    def test_slider_to_dict(self):
        """should convert to dict ready for messages"""
        expected_dict = {
            "Slider": {
                "title": "SliderTitle",
                "icon": "IconStrValue",
                "min_value": 0,
                "max_value": 1000,
                "init_value": 100,
                "value": 100,
            }
        }
        check.equal(self.slider.dict(), expected_dict)

    def test_slider_set_value(self):
        """should clip given value to valid range"""
        self.slider.value = self.slider.max_value + 1
        check.equal(self.slider.value, self.slider.max_value)
        self.slider.value = self.slider.min_value - 1
        check.equal(self.slider.value, self.slider.min_value)
        average = (self.slider.min_value + self.slider.max_value) / 2
        self.slider.value = average
        check.equal(self.slider.value, average)
