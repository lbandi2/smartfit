#!/bin/bash

mkdir -p logs
cd /home/sergio/scripts/smartfit/
. ./env/bin/activate
/home/sergio/scripts/smartfit/env/bin/python3 /home/sergio/scripts/smartfit/main.py >> logs/smartfit-"`date +"%Y-%m-%d_%H.%M.%S"`".log 2>&1
deactivate
