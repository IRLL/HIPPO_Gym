import logging
import sys
import time

from hippogym import HippoGym
from hippogym.ui_elements.control_panel import ControlPanel, Button
from lunar_lander import play

logging.basicConfig(level=logging.DEBUG)


def main():
    hippo = HippoGym()

    hippo.standby()
    # Start Phase 1, play game
    group = hippo.group(12)
    print(group)
    play(hippo)

    # Start Phase 2
    buttons = [
        Button(text="Finish", color="white", bgcolor="red", value="end"),
        Button(text="Run", color="white", bgcolor="green", value="run"),
        Button(text="Hide Game Window", color="white", bgcolor="blue", value="hide"),
        Button(text="Show Game Window", color="white", bgcolor="blue", value="show"),
    ]
    control = ControlPanel(hippo.queues["control_q"], buttons=buttons)
    hippo.set_control_panel(control)

    info = hippo.get_info_panel()
    info.reset()
    window = hippo.get_game_window()
    textbox = hippo.add_text_box()
    textbox.update(text="Input Code Here")
    hippo.start()
    while not hippo.stop:
        if get_run(hippo):
            textbox.request()
            time.sleep(0.1)
            textbox.hide()
            do_stuff(textbox, window, info)
            textbox.send()
        time.sleep(0.1)
    print("All Done")
    hippo.disconnect()
    exit()


def do_stuff(textbox, window, info):
    window.send()
    text = textbox.get_text()
    print(text)
    try:
        text.append(33)
    except Exception as e:
        error = f"{sys.exc_info()}"
        info.update(text=error)
    time.sleep(2)


def get_run(hippo: HippoGym):
    for item in hippo.poll():
        button = item.get("BUTTONPRESSED", None)
        if button == "run":
            return True
        if button == "hide":
            hippo.get_game_window().hide()
        if button == "hide":
            hippo.get_game_window().send()
    return False


if __name__ == "__main__":
    main()
