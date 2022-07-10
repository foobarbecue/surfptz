##2022-07-09
Looking at Bescor yaw range & initialization. Clockwise, (yaw_relays[0] direction) it hits a hard stop at 345 deg. Counterclockwise, it goes past 360 and hits a hard stop around 355. A full rotation at max speed takes about 46 seconds.

Same for pitch. Takes about 14 seconds to go from min to max. On the IMU this is from -12.5 to 13.3 deg.

Trying to set up compass-based pointing but not getting anything back from imu.get_magnetic_vector()