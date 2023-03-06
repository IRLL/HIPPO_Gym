from examples.minigrid_example import build_experiment
from tests.end_to_end.custom_checks import check_ui_elements


def test_minigrid_ui_elements(unused_tcp_port: int):
    """minigrid example should start a trial on connexion and give expected UIElements"""
    hippo = build_experiment()
    expected_ui_elements = ("InfoPanel", "GameWindow", "ControlPanel")
    check_ui_elements(hippo, expected_ui_elements, unused_tcp_port)
