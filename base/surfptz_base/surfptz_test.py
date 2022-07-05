from gimbal import BescorGimbal
from panasonic_camera import camera_manager
import logging
from time import sleep


logging.basicConfig(level=logging.INFO)


camera_mgr = camera_manager.PanasonicCameraManager(identify_as='surfptz')

camera_mgr.start()
# camera_mgr.run()

bescor_gimbal = BescorGimbal()

while True:
    camera_mgr.camera.zoom_in_slow()
    bescor_gimbal.goto(pitch_angle=5, yaw_angle=5)
    camera_mgr.camera.zoom_out_slow()
    bescor_gimbal.goto(pitch_angle=0, yaw_angle=0)