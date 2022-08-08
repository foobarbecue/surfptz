#!/bin/bash
echo starting surfptz
#source /home/aaron/robot-cameraman-venv/bin/activate
rfcomm release 00:0C:BF:16:58:31
rfcomm bind rfcomm0 00:0C:BF:16:58:31
export PYTHONPATH=/home/aaron/surfptz/base/surfptz_base/
export FLASK_APP=/home/aaron/surfptz/base/surfptz_base/server.py
#python -m robot_cameraman --gimbal Bescor --detectionEngine Dummy --identifyToPanasonicCameraAs surfptz
python -m flask run --host=0.0.0.0