import logging
from time import sleep
import math

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
        # CCW 345->0aka360->355 , CW 355->360aka0->345
        self.yaw_relays = [LED("BOARD31"), LED("BOARD33")]
        # down, up
        self.pitch_relays = [LED("BOARD35"), LED("BOARD37")]
        # TODO intelligently find IMU device path
        self.imu = IMU(path='/dev/rfcomm0', baudrate=115200)
        self.update_interval: float = 0.5
        self.yaw_target_reached: bool = True
        self.pitch_target_reached: bool = True
        self._imu_yaw_at_max_cw = None
        self._imu_yaw_at_max_ccw = None
        self._imu_pitch_at_max = None
        self._imu_pitch_at_min = None
        # hard-coded to san clemente for now
        self._declination = 11.36

    def __del__(self):
        logger.info('Stopping gimbal motion')
        self.stop()
        logger.info('Freeing gimbal GPIOs')
        [yr.close() for yr in self.yaw_relays + self.pitch_relays]
        logger.info('Disconnecting from IMU')
        self.imu.close()

    def initialize(self):

        # PITCH
        logger.info('Finding pitch range')
        self.pitch_relays[0].on()
        sleep(20)
        self.pitch_relays[0].off()
        self._imu_pitch_at_min = self.imu.last_pitch
        self.pitch_relays[1].on()
        sleep(20)
        self.pitch_relays[1].off()
        self._imu_pitch_at_max = self.imu.last_pitch

        # YAW
        logger.info('Finding yaw range')
        self.yaw_relays[1].on()
        sleep(50)
        self.yaw_relays[1].off()
        self._imu_yaw_at_max_cw = self.imu.last_yaw
        self.yaw_relays[0].on()
        sleep(50)
        self.yaw_relays[0].off()
        self._imu_yaw_at_max_ccw = self.imu.last_yaw

    def goto(
            self,
            yaw_angle: float,
            pitch_angle: float,
    ) -> None:
        self.yaw_target_reached = False
        self.pitch_target_reached = False
        while not (self.yaw_target_reached and self.pitch_target_reached):
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
            self.yaw_target_reached = True

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
            self.pitch_target_reached = True

    def stop(self) -> None:
        for relay in self.yaw_relays + self.pitch_relays:
            relay.off()

    def get_angles(self):
        # TODO incorporate magnetometer
        return self.imu.get_angle()
    
    def set_declination(self):
        raise NotImplementedError

    @staticmethod
    def _xy_to_az(x: float, y: float) -> float:
        """
        Given relative coordinates, return a 0 to 360 azimuth angle
        """
        az = math.degrees(math.atan2(y, x))
        if az < 0:
            az += 360
        return az

    def point_at_rel_coords(self, northing: float, easting: float, elevation: float) -> None:
        yaw_angle = self._xy_to_az(x=easting, y=northing)
        yaw_angle -= self._declination
        if yaw_angle < 0:
            yaw_angle += 360
        distance = math.sqrt(northing ** 2 + easting ** 2 + elevation ** 2)
        pitch_angle = math.asin(elevation / distance)
        self.control(yaw_angle=yaw_angle, pitch_angle=pitch_angle)
