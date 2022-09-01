import os
import base64
import yaml
import logging

import numpy as np
from PIL import Image
from io import BytesIO


def load_config() -> dict:
    logging.info("Loading Config in trial.py")
    try:
        with open(".trialConfig.yml", "r") as infile:
            config = yaml.load(infile, Loader=yaml.FullLoader)
    except FileNotFoundError:
        with open(os.path.join("App", ".trialConfig.yml"), "r") as infile:
            config = yaml.load(infile, Loader=yaml.FullLoader)
    logging.info("Config loaded in trial.py")
    return config.get("trial")


def load_to_b64(path: str) -> str:
    img = Image.open(path)
    img = alpha_to_color(img.convert("RGBA"))
    return array_to_b64(np.array(img))


def array_to_b64(img_array) -> str:
    try:
        img = Image.fromarray(img_array, mode="RGB")
        fp = BytesIO()
        img.save(fp, format="JPEG", quality="web_high")
        frame = base64.b64encode(fp.getvalue()).decode("utf-8")
        fp.close()
    except:
        raise TypeError(
            "Render failed. Is env.render('rgb_array') being called"
            " with the correct arguement?"
        )
    return frame


def alpha_to_color(image, color=(255, 255, 255)):
    """Alpha composite an RGBA Image with a specified color.

    Source: http://stackoverflow.com/a/9459208/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """
    image.load()  # needed for split()
    background = Image.new("RGB", image.size, color)
    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
    return background
