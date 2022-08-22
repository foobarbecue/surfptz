import logging
from time import sleep
import math
from typing import Tuple

from pyproj import Transformer

logger: logging.Logger = logging.getLogger(__name__)

def to_0_360(angle):
    if angle < 0:
        return angle + 360
    else:
        return angle

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
        self._declination = 11.46 # San Clemente 2022 magnetic declination
        self._imu_yaw_at_max_cw = None
        self._imu_yaw_at_max_ccw = None
        self._imu_pitch_at_max = None
        self._imu_pitch_at_min = None
        # hard-coded to san clemente for now
        self._declination = 11.36
        self._origin_latlon = None

    def __del__(self):
        logger.info('Stopping gimbal motion')
        self.stop()
        logger.info('Freeing gimbal GPIOs')
        [yr.close() for yr in self.yaw_relays + self.pitch_relays]
        logger.info('Disconnecting from IMU')
        self.imu.close()

    def get_bearing(self):
        return to_0_360(self.imu.last_yaw) + self._declination
    
    def log_gimbal_and_sleep(self, total_time_s, interval_s=0.5):
        for ind in range(0, math.ceil(total_time_s / interval_s)):
            logger.info(f'yaw: {to_0_360(self.imu.last_yaw)}, pitch: {self.imu.last_pitch}')
            sleep(interval_s)

    def is_in_yaw_deadzone(self, angle) -> bool:
        """
        The Bescor gimbal cannot get to about 10 degrees of the circle.
        This function returns False if we are in that "deadzone"
        """
        if self._imu_yaw_at_max_cw < self._imu_yaw_at_max_ccw:
            return not (self._imu_yaw_at_max_cw
                        < angle
                        < self._imu_yaw_at_max_ccw)
        else:
            #There is a zero-crossing in the deadzone (e.g. CW limit 355, CCW 5)
            return (self._imu_yaw_at_max_cw < angle) or\
                   (angle < self._imu_yaw_at_max_ccw)

    def initialize(self):

        # PITCH
        logger.info('Finding pitch range')
        self.pitch_relays[0].on()
        self.log_gimbal_and_sleep(20)
        self.pitch_relays[0].off()
        self._imu_pitch_at_min = self.imu.last_pitch
        self.pitch_relays[1].on()
        self.log_gimbal_and_sleep(20)
        self.pitch_relays[1].off()
        self._imu_pitch_at_max = self.imu.last_pitch

        # YAW
        logger.info('Finding yaw range')
        self.yaw_relays[1].on()
        self.log_gimbal_and_sleep(50)
        self.yaw_relays[1].off()
        self._imu_yaw_at_max_cw = to_0_360(self.imu.last_yaw)
        self.yaw_relays[0].on()
        self.log_gimbal_and_sleep(50)
        self.yaw_relays[0].off()
        self._imu_yaw_at_max_ccw = to_0_360(self.imu.last_yaw)

        logger.info(f'Pitch range found to be'
                    f'{self._imu_pitch_at_min} '
                    f'to {self._imu_pitch_at_max}')
        logger.info(f'Yaw max found to be: '
                    f'{self._imu_yaw_at_max_cw} clockwise, and '
                    f'to {self._imu_yaw_at_max_ccw} counterclockwise.')

    def set_origin(self, lon, lat):
        self._origin_latlon = (lon, lat)

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
                # Check if the gimbal can get to this yaw
                if self.is_in_yaw_deadzone(yaw_angle):
                    self.control(yaw_angle=yaw_angle, pitch_angle=pitch_angle)
                else:
                    logger.info(f"desired yaw is in deadzone")
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

        z_angle = self.get_bearing()
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
    
    def set_declination(self, declination):
        self._declination = declination

    @staticmethod
    def _xy_to_az(x: float, y: float) -> float:
        """
        Given relative coordinates, return a 0 to 360 azimuth angle
        """
        az = math.degrees(math.atan2(x, y))
        if az < 0:
            az += 360
        return az
    
    def calculate_relcoords(self, lat: float, lon: float) -> Tuple[float, float]:
        """
        Determine the N, E offset in meters from origin_latlon to latest_latlon
        """

        # Todo cache this Transformer instead of creating every time
        xfrmr = Transformer.from_crs(4326,f"+proj=tmerc "
                                          f"+lat_0={self._origin_latlon[0]} "
                                          f"+lon_0={self._origin_latlon[1]}")

        # Convert origin to transverse mercator centered on origin
        origin_m = xfrmr.transform(self._origin_latlon[1],
                                   self._origin_latlon[0])
        logger.info(f'origin: origin_m')

        # Convert latest_latlon to same
        new_m = xfrmr.transform(lon, lat)

        # Subtract them
        return (new_m[1]- origin_m[1], new_m[0] - origin_m[0])

    def point_at_rel_coords(self, northing: float, easting: float, elevation=None) -> None:
        yaw_angle = self._xy_to_az(x=easting, y=northing)
        yaw_angle -= self._declination
        if yaw_angle < 0:
            yaw_angle += 360
        if elevation:
            distance = math.sqrt(northing ** 2 + easting ** 2 + elevation ** 2)
            pitch_angle = math.asin(elevation / distance)
        else:
            # If we weren't given an elevation, leave pitch where it is
            pitch_angle = self.imu.last_pitch
        logger.info(f'Given rel coords '
                    f'N: {northing} E: {easting} El:{elevation}, '
                    f'going to point at yaw: {yaw_angle} pitch: {pitch_angle}')
        self.goto(yaw_angle=yaw_angle, pitch_angle=pitch_angle)

    def point_at_abs_coords(self, lat: float, lon: float) -> None:
        e, n = self.calculate_relcoords(lat=lat, lon=lon)
        logger.info(f'Calculated northing {n}, easting {e} from'
                    f' rel lat {lat} lon {lon}')
        #TODO declination
        #TODO elevation
        self.point_at_rel_coords(northing=n, easting=e, elevation=0)