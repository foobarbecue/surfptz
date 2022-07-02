from flask import Flask, Response, request, redirect, jsonify

app = Flask(__name__,
            static_url_path='',
            static_folder=Path(__file__).parent / 'server_static_folder')


@app.route('/')
def index():
    return redirect('index.html')

@app.route('/api/angle')
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
    logger.debug(f'angle pan={pan_angle} tilt={tilt_angle}')
    cameraman_mode_manager.angle(pan_angle=pan_angle, tilt_angle=tilt_angle)
    return '', 204