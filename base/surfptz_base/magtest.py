import math, time
from witmotion import IMU
imu = IMU(path='/dev/rfcomm0', baudrate=115200)


while True:
    time.sleep(1)
    # last_msg is a typo for last_mag. PR here: https://github.com/storborg/witmotion/pull/5
    mag_reading = imu.last_msg
    az = math.atan2(mag_reading[0], mag_reading[1]) * 180 / math.pi
    print(az)
