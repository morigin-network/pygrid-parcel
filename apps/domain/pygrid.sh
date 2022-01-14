#!/bin/bash
WORKDIR="/home/thomas/PyGrid"
cd "$WORKDIR"/apps/domain && /home/thomas/anaconda3/envs/pygrid/bin/poetry run python ./src/__main__.py --name bob --port 7001 --start_local_db

