import logging
from time import sleep

logger: logging.Logger = logging.getLogger(__name__)

class BescorGimbal:
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
        self.update_interval: float = 0.5
        self.target_reached: bool = True

    def goto(
            self,
            yaw_angle: float,
            pitch_angle: float,
    ) -> None:
        self.target_reached = False
        while not self.target_reached:
            # Check that there is IMU data when we command any movement
            if self.imu.last_a:
                self.control(yaw_angle=yaw_angle, pitch_angle=pitch_angle)
            else:
                logger.info(f"no imu data")
                self.stop()
            sleep(self.update_interval)

    # Only supports angle mode
    def control(
            self,
            yaw_angle: float,
            pitch_angle: float,
    ) -> None:
        """
        Set the relays controlling the Bescor gimbal to the correct values to
        move towards desired yaw and pitch angle.
        """
        logger.info(f'Going to yaw:{yaw_angle} pitch:{pitch_angle}')

        # Rename variables for clarity
        desired_yaw = yaw_angle
        desired_pitch = pitch_angle

        z_angle = self.imu.last_yaw
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

        y_angle = self.imu.last_pitch
        y_err = y_angle - desired_pitch
        if abs(y_err) > self.deadband:
            if y_err > 0:
                self.pitch_relays[0].on()
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