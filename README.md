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

HippoGym is a framework for simplifying human-ai interaction research over the web.
The platform provides a communicator that opens a websocket to pass environment information to a browser-based front-end and recieve commands and actions from the front end.

Built in Python, the framework is designed as a bring-your-own agent system where the framework provides an easy to impliment middle layer between a researcher's existing agent and a human interacting over the web. The framework is naive in that it makes no assumptions about how human input will be used, it simply provides the mechanism to pass along and record this information.


The HippoGym Project contains 4 repositories:

1.  The main framework: [HIPPO_Gym](https://github.com/IRLL/HIPPO_Gym)

2.  The AWS code and instructions: [HIPPO_Gym_AWS](https://github.com/IRLL/HIPPO_Gym_AWS)

3.  The React Front End: [HIPPO_Gym_React_FrontEnd](https://github.com/IRLL/HIPPO_Gym_FrontEnd_React)

4.  The SSL Certificate Getter: [HIPPO_Gym_SSL](https://github.com/IRLL/HIPPO_Gym_SSL)

For members of the IRLL or anyone whose organization has already setup the AWS infrastructure, the only repo required is #1.

Anyone is welcome to use the front-end deployed to [irll.net](https://irll.net)


## Intallation

```bash
pip install hippogym
```

## Use

See [examples](https://github.com/IRLL/HIPPO_Gym/tree/master/examples)


