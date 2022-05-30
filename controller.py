from witmotion import IMU
from time import sleep
from gpiozero import LED
from time import sleep

# positive direction first
azimuth = [LED("BOARD31"), LED("BOARD33")]
elevation = [LED("BOARD35"), LED("BOARD37")]

imu = IMU(baudrate=115200)

def go_to_setpoint(setpoint, deadband):
    try:
        while True:
            sleep(0.2)
            y_angle = imu.get_angle()[1]
            y_err = y_angle - setpoint
            if abs(y_err) > deadband:
                if y_err > 0:
                    elevation[0].on()
                    print(f'error {y_err}, moving el0')
                else:
                    elevation[1].on()
                    print(f'error {y_err}, moving el1')
            else:
                [relay.off() for relay in elevation]
                print(f'error {y_err}, within deadband')
    finally:
        [relay.off() for relay in elevation]

go_to_setpoint(10, 2)