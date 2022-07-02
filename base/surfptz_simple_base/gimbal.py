from witmotion import IMU
from time import sleep
from gpiozero import LED
from time import sleep

class BescorGimbal(Gimbal):
    """
    This gimbal class is for use with this combination of products:
     - Bescor MP-101 Pan & Tilt Head
     - Witmotion BWT901CL intertial motion unit
     - Relay 4 Zero 3V 4 Channel Relay Shield for Raspberry Pi
    """
    def __init__(self):
        from gpiozero import LED
        from witmotion import IMU
        self.deadband: float = 2
        self.yaw_relays = [LED("BOARD31"), LED("BOARD33")]
        self.pitch_relays = [LED("BOARD35"), LED("BOARD37")]
        # TODO intelligently find IMU device path
        self.imu = IMU(path='/dev/rfcomm0', baudrate=115200)
        self.update_interval: float = 0.1

    # Only supports angle mode
    def control(
            self,
            yaw_mode: ControlMode = ControlMode.speed,
            yaw_speed: float = 0,
            yaw_angle: float = 0,
            pitch_mode: ControlMode = ControlMode.speed,
            pitch_speed: float = 0,
            pitch_angle: float = 0,
            roll_mode: ControlMode = ControlMode.speed,
            roll_speed: float = 0,
            roll_angle: float = 0) -> None:
        """
        Set the relays controlling the Bescor gimbal to the correct values to
        move towards desired yaw and pitch angle.
        """
        logger.info('Bescor control called')

        # Rename variables for clarity
        desired_yaw = yaw_angle
        desired_pitch = pitch_angle

        z_angle = self.imu.get_angle()[2]
        z_err = z_angle - desired_yaw
        if abs(z_err) > self.deadband:
            if z_err > 0:
                self.yaw_relays[0].on()
                logger.info(f'z error {z_err}, moving yaw0')
            else:
                self.yaw_relays[1].on()
                logger.info(f'z error {z_err}, moving yaw1')
        else:
            for relay in self.yaw_relays:
                relay.off()
            logger.info(f'z error {z_err}, within deadband')

        y_angle = self.imu.get_angle()[1]
        y_err = y_angle - desired_pitch
        if abs(y_err) > self.deadband:
            if y_err > 0:
                self.yaw_relays[0].on()
                logger.info(f'y error {y_err}, moving pitch0')
            else:
                self.pitch_relays[1].on()
                logger.info(f'y error {y_err}, moving pitch1')
        else:
            for relay in self.pitch_relays:
                relay.off()
            logger.info(f'y error {y_err}, within deadband')

    def stop(self) -> None:
        for relay in self.yaw_relays + self.pitch_relays:
            relay.off()

    def get_angles(self):
        return self.imu.get_angle()