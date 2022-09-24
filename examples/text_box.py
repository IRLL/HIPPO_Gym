import asyncio
import base64
import logging
from typing import List, Optional

from hippogym.hippogym import HippoGym
from hippogym.trialsteps import InteractiveStep
from hippogym.ui_elements import (
    InfoPanel,
    TextBox,
    ControlPanel,
    GameWindow,
    image_sliders,
    standard_controls,
)

# from hippogym.recorder.recorder import Recorder

logging.basicConfig(level=10)


class TextBoxStep(InteractiveStep):
    def __init__(self, images_paths: List[str]) -> None:
        self.index = 0
        self.images = []
        for img_path in images_paths:
            self.images.append(get_image(img_path))

        self.info_panel = InfoPanel()
        self.text_box = TextBox(text="Hello World!", buttons=["save", "run", "clear"])
        self.control_panel = ControlPanel(buttons=standard_controls)
        self.game_window = GameWindow(image=self.current_image, width=300, height=300)

        ui_elements = [
            self.info_panel,
            self.text_box,
            self.control_panel,
            self.game_window,
        ]

        super().__init__(ui_elements=ui_elements)

    @property
    def current_image(self):
        return self.images[self.index % len(self.images)]

    def run(self) -> None:
        toggle_info = True
        toggle_sliders = True
        while True:
            for item in self.poll():
                button = item.get("BUTTONPRESSED", None)
                if button == "save":
                    self.text_box.request()
                    text = self.text_box.get_text()
                    # json_recorder.record({"text": text})
                    # pickle_recorder.record({"text": text})
                action = item.get("ACTION", None)
                if action == "right":
                    self.index += 1
                    self.game_window.update(image=self.current_image)
                    self.control_panel.send()
                elif action == "left":
                    self.index -= 1
                    self.game_window.update(image=self.current_image)
                elif action == "up":
                    if toggle_sliders:
                        self.control_panel.update(sliders=image_sliders)
                    else:
                        self.control_panel.update(sliders=[])
                    toggle_sliders = not toggle_sliders
                elif action == "down":
                    if toggle_info:
                        self.info_panel.update(
                            text="Hello world!",
                            items=[1],
                            key_value={"hi": "there", "dear": "human"},
                        )
                    else:
                        self.info_panel.update(text="", items=[], key_value={})
                    toggle_info = not toggle_info
                elif action == "fire":
                    self.text_box.send()


def get_image(filename):
    with open(f"img/{filename}", "rb") as infile:
        frame = base64.b64encode(infile.read()).decode("utf-8")
    return frame


def build_experiment() -> HippoGym:
    images_paths = [
        "logo_vertical.png",
        "icon_dark.png",
        "words_horizontal.png",
        "logo_horizontal.png",
        "icon_light.png",
        "words_vertical.png",
    ]
    # json_recorder = Recorder(mode="json", clean_path=True)
    # pickle_recorder = Recorder(mode="pickle")
    text_box_step = TextBoxStep(images_paths)
    return HippoGym(text_box_step)


def main():
    hippo = build_experiment()
    hippo.start()


if __name__ == "__main__":
    main()
