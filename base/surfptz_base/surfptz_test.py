from gimbal import BescorGimbal
# import camera_manager
import logging
from time import sleep


logging.basicConfig(level=logging.INFO)


# camera_mgr = camera_manager.PanasonicCameraManager(identify_as='surfptz')

bescor_gimbal = BescorGimbal()

bescor_gimbal.goto(pitch_angle=0, yaw_angle=0)