from examples.hcraft_example import build_experiment
from tests.end_to_end.custom_checks import check_ui_elements


def test_crafting_ui_elements(unused_tcp_port: int):
    hippo = build_experiment(render_mode="console")
    expected_ui_elements = ("GameWindow",)
    check_ui_elements(hippo, expected_ui_elements, unused_tcp_port)
