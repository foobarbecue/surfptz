from witmotion import IMU
from time import sleep
from gpiozero import LED
from time import sleep

# positive direction first
azimuth = [LED("BOARD31"), LED("BOARD33")]
elevation = [LED("BOARD35"), LED("BOARD37")]

imu = IMU(baudrate=115200)

def stop_all():
    [relay.off() for relay in elevation + azimuth]

def go_to_setpoint(az, el, deadband):
    try:
        while True:
            sleep(0.2)

            z_angle = imu.get_angle()[2]
            z_err = z_angle - az
            if abs(z_err) > deadband:
                if z_err > 0:
                    azimuth[0].on()
                    print(f'z error {z_err}, moving az0')
                else:
                    azimuth[1].on()
                    print(f'z error {z_err}, moving az1')
            else:
                [relay.off() for relay in azimuth]
                print(f'z error {z_err}, within deadband')

            y_angle = imu.get_angle()[1]
            y_err = y_angle - el
            if abs(y_err) > deadband:
                if y_err > 0:
                    elevation[0].on()
                    print(f'y error {y_err}, moving el0')
                else:
                    elevation[1].on()
                    print(f'y error {y_err}, moving el1')
            else:
                [relay.off() for relay in elevation]
                print(f'y error {y_err}, within deadband')

    finally:
        [relay.off() for relay in elevation]

go_to_setpoint(10, 10, 2)