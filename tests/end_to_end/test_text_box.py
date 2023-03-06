from examples.text_box import build_experiment

from tests.end_to_end.custom_checks import check_ui_elements


def test_text_box_ui_elements(unused_tcp_port: int):
    hippo = build_experiment()
    expected_ui_elements = ("InfoPanel", "TextBox", "ControlPanel", "GameWindow")
    check_ui_elements(hippo, expected_ui_elements, unused_tcp_port)
