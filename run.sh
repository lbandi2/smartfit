#!/bin/bash

mkdir -p logs
find logs -type f -mtime +30 -delete # delete files older than 30 days
cd /home/sergio/scripts/smartfit/
. ./env/bin/activate
/home/sergio/scripts/smartfit/env/bin/python3 /home/sergio/scripts/smartfit/main.py >> logs/smartfit-"`date +"%Y-%m-%d_%H.%M.%S"`".log 2>&1
deactivate
