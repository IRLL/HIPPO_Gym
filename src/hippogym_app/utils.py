import os
import base64
import yaml
import logging

import numpy as np
from PIL import Image
from io import BytesIO


def load_config(config_path: str) -> dict:
    with open(config_path, "r") as infile:
        config: dict = yaml.load(infile, Loader=yaml.FullLoader)
    logging.info("Trial config loaded from %s", config_path)
    return config.get("trial")


def load_to_b64(path: str) -> str:
    img = Image.open(path)
    img = alpha_to_color(img.convert("RGBA"))
    return array_to_b64(np.array(img))


def array_to_b64(img_array) -> str:
    try:
        img = Image.fromarray(img_array, mode="RGB")
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality="web_low")
        frame = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()
    except Exception as error:
        raise TypeError(
            "Render failed. Is env.render('rgb_array') being called"
            " with the correct arguments?"
        ) from error
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
