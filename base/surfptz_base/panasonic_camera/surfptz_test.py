from gimbal import BescorGimbal
import camera_manager

camera_mgr = camera_manager.PanasonicCameraManager(identify_as='surfptz')
bescor_gimbal = BescorGimbal()
bescor_gimbal.control(pitch_angle=0, yaw_angle=0)