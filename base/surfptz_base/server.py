import logging

from flask import Flask, Response, request, redirect, jsonify
from gimbal import BescorGimbal
from panasonic_camera import camera_manager
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

#camera_mgr = camera_manager.PanasonicCameraManager(identify_as='surfptz')
#camera_mgr.start()

@app.route('/api/initialize')
def initialize():
    gimbal.initialize()
    return '', 204

@app.route('/api/angle')
def angle():
    gimbal = BescorGimbal()
    if 'pan' not in request.args:
        return "Missing query parameter 'pan'", 400
    if 'tilt' not in request.args:
        return "Missing query parameter 'tilt'", 400
    try:
        pan_angle = int(request.args.get('pan'))
    except ValueError:
        return "Query parameter 'pan' should be a number", 400
    try:
        tilt_angle = int(request.args.get('tilt'))
    except ValueError:
        return "Query parameter 'tilt' should be a number", 400
    logging.debug(f'angle pan={pan_angle} tilt={tilt_angle}')
    gimbal.goto(pitch_angle=tilt_angle, yaw_angle=pan_angle)
    return '', 204