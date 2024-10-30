#!/usr/bin/env bash

export PYTHONPATH="/project/src:$PYTHONPATH"

cd /project/src
python shell/api/main.py