import logging

from flask import Flask, Response, request, redirect, jsonify
from gimbal import BescorGimbal
from panasonic_camera import camera_manager
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

camera_mgr = camera_manager.PanasonicCameraManager(identify_as='surfptz')
camera_mgr.start()
gimbal = BescorGimbal()

@app.route('/api/initialize', methods=['POST', 'GET'])
def initialize():
    gimbal.initialize()
    return '', 204

@app.route('/api/angle', methods=['POST', 'GET'])
def angle():
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

@app.route('/api/zoom_in', methods=['POST', 'GET'])
def zoom_in_slow():
    camera_mgr.camera.zoom_in_slow()
    return '', 204
    
@app.route('/api/zoom_out', methods=['POST', 'GET'])
def zoom_out():
    camera_mgr.camera.zoom_out_slow()
    return '', 204

@app.route('/api/zoom_stop', methods=['POST', 'GET'])
def zoom_stop():
    camera_mgr.camera.zoom_stop()
    return '', 204

@app.route('/api/start_recording', methods=['POST', 'GET'])
def video_recstart():
    camera_mgr.camera.video_recstart()
    return '', 204

@app.route('/api/stop_recording', methods=['POST', 'GET'])
def video_recstop():
    camera_mgr.camera.video_recstop()
    return '', 204

@app.route('/api/set_declination', methods=['POST', 'GET'])
def set_declination():
    raise NotImplementedError

@app.route('/api/get_angles', methods=['POST', 'GET'])
def get_angles():
    angles = gimbal.get_angles()
    return f"{angles}", 200

@app.route('/api/relcoords', methods=['POST', 'GET'])
def relative_coordinates():
    """
    API route causing the gimbal to point at coordinates specified in meters.
    """
    if 'n' not in request.args:
        return "Missing query parameter 'n'", 400
    if 'e' not in request.args:
        return "Missing query parameter 'e'", 400
    if 'el' not in request.args:
        return "Missing query parameter 'el'", 400
    try:
        northing = float(request.args.get('n'))
    except ValueError:
        return "Query parameter 'n' should be a number", 400
    try:
        easting = float(request.args.get('e'))
    except ValueError:
        return "Query parameter 'e' should be a number", 400
    try:
        elevation = float(request.args.get('el'))
    except ValueError:
        return "Query parameter 'el' should be a number", 400
    logging.debug(f'northing={northing} easting={easting} elevation={elevation}')
    gimbal.point_at_rel_coords(
        northing=northing, easting=easting, elevation=elevation
    )
    return '', 204

@app.route('/api/set_origin', methods=['POST', 'GET'])
def set_origin():
    if 'lat' not in request.args:
        return "Missing query parameter 'lat'", 400
    if 'lon' not in request.args:
        return "Missing query parameter 'lon'", 400

    try:
        lat = float(request.args.get('lat'))
    except ValueError:
        return "Query parameter 'lat' should be a number", 400
    try:
        lon = float(request.args.get('lon'))
    except ValueError:
        return "Query parameter 'lon' should be a number", 400
    logging.debug(f'lat={lat} lon={lon}')
    
    gimbal.set_origin(lat=lat, lon=lon)
    return '', 204

@app.route('/api/abscoords', methods=['POST', 'GET'])
def absolute_coordinates():
    if 'lat' not in request.args:
        return "Missing query parameter 'lat'", 400
    if 'lon' not in request.args:
        return "Missing query parameter 'lon'", 400

    try:
        lat = float(request.args.get('lat'))
    except ValueError:
        return "Query parameter 'lat' should be a number", 400
    try:
        lon = float(request.args.get('lon'))
    except ValueError:
        return "Query parameter 'lon' should be a number", 400
    logging.debug(f'lat={lat} lon={lon}')

    gimbal.set_origin(lat=lat, lon=lon)
    return '', 204