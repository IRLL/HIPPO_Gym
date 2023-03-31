# HippoGym

##### Human Input Parsing Platform for Openai Gym

[![Fury - PyPi stable version](https://badge.fury.io/py/hippogym.svg)](https://badge.fury.io/py/hippogym)
[![PePy - Downloads](https://static.pepy.tech/badge/hippogym)](https://pepy.tech/project/hippogym)
[![PePy - Downloads per week](https://static.pepy.tech/badge/hippogym/week)](https://pepy.tech/project/hippogym)

[![Codacy - grade](https://app.codacy.com/project/badge/Grade/dcd52445bb314a0798151a2f2bc308f6)](https://www.codacy.com/gh/IRLL/HIPPO_Gym/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=IRLL/HIPPO_Gym&amp;utm_campaign=Badge_Grade)
[![Codacy - coverage](https://app.codacy.com/project/badge/Coverage/dcd52445bb314a0798151a2f2bc308f6)](https://www.codacy.com/gh/IRLL/HIPPO_Gym/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=IRLL/HIPPO_Gym&amp;utm_campaign=Badge_Coverage)
[![CodeStyle - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CodeStyle - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

## Purpose:

HippoGym is a python library for simplifying human-ai interaction research over the web.
The library provides a communicator that opens a websocket to pass environment information and recieve commands and actions from browser-based front-end.

The library is designed to be customizable for diverse research applications. The framework is naive in that it makes no assumptions about how human or agents input will be used, it simply provides the mechanism to pass along and record this information.


## Installation

```bash
pip install hippogym
```

## Examples

### Lunar Lander with human agent
Copy and run the [lunar lander example](https://github.com/IRLL/HIPPO_Gym/blob/master/examples/lunar_lander.py).

You should see:
![Backend log success lunar](docs/backend_success_example.png)

Then connect a client to the websocket using the host and port, you can use the irll frontend: https://beta.irll.net/?server=ws://localhost:5000

You can now play with either the command pannel or the keyboard:
![Frontend display lunar](docs/lunar_human_demo.gif)

### Minigrid with human agent
Copy and run the [minigrid example](https://github.com/IRLL/HIPPO_Gym/blob/master/examples/minigrid_example.py).

You should see:
![Backend log success minigrid](docs/backend_success_example.png)

Then connect a client to the websocket using the host and port, you can use the irll frontend: https://beta.irll.net/?server=ws://localhost:5000

You can now play with either the command pannel or the keyboard:
![Frontend display minigrid](docs/minigrid_human_demo.gif)

