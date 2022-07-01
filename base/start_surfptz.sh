#!/bin/bash
echo starting surfptz
#source /home/aaron/robot-cameraman-venv/bin/activate
rfcomm release 00:0C:BF:16:58:31
rfcomm bind rfcomm0 00:0C:BF:16:58:31
export PYTHONPATH=/home/aaron/robot-cameraman
python -m robot_cameraman --gimbal Bescor --detectionEngine Dummy --identifyToPanasonicCameraAs surfptz
