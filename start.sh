#!/bin/bash
export PYTHONPATH=/src:/src/hippogym:$PYTHONPATH

xvfb-run -s "-screen 0 1400x900x24" python3 /src/hippogym/examples/minigrid_example.py