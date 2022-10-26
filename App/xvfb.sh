#! /bin/bash

xvfb-run -s "-screen 0 1400x900x24" python3 communicator.py dev #add 'dev' at the end of this line to disable ssl and s3 uploading for testing. Remove 'dev' for deployment
