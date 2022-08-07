from kivy.lang import Builder
from plyer import gps
from kivy.app import App
from kivy.properties import StringProperty
from kivy.clock import mainthread
from kivy.utils import platform
import requests
import json
from datetime import datetime


class SurfptzTagApp(App):

    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')
    dest_addrs = {
        'Base': 'http://10.128.0.1/api/relcoords',
        'Firebase': 'https://surfptz-default-rtdb.firebaseio.com/.json'
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dest_addr = None
        self._latest_latlon = None
    
    def set_dest_addr(self, dest):
        self.dest_addr = self.dest_addrs[dest]
    
    def set_origin(self):
        requests.post(url='http://10.128.0.1/api/set_origin', data=self._latest_latlon)
    
    def request_android_permissions(self):
        """
        Since API 23, Android requires permission to be requested at runtime.
        This function requests permission and handles the response via a
        callback.

        The request will produce a popup if permissions have not already been
        been granted, otherwise it will do nothing.
        """
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            """
            Defines the callback to be fired when runtime permission
            has been granted or denied. This is not strictly required,
            but added for the sake of completeness.
            """
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)
        # # To request permissions without a callback, do:
        # request_permissions([Permission.ACCESS_COARSE_LOCATION,
        #                      Permission.ACCESS_FINE_LOCATION])

    def build(self):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'

        if platform == "android":
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()
            self.start(1000,0)

        return Builder.load_file('SurfptzTag.kv')

    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()

    @mainthread
    def on_location(self, **kwargs):
        self.gps_location = '\n'.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])
        self._latest_latlon = (kwargs['lat'], kwargs['lon'])
        timestamp = datetime.now().isoformat()
        gps_data = json.dumps({timestamp : kwargs})
        if self.dest_addr:
            requests.post(
                url=self.dest_addr,
                data=json.dumps(gps_data)
            )

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def on_pause(self):
        gps.stop()
        return True

    def on_resume(self):
        gps.start(1000, 0)
        pass


if __name__ == '__main__':
    SurfptzTagApp().run()
