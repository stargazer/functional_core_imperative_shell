#!/usr/bin/env bash

export PYTHONPATH="/project/app:$PYTHONPATH"

cd /project/src
python shell/scripts/print_tasks.py