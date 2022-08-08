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
    gps_status = StringProperty('Click Start to send GPS location updates')
    dest_addrs = {
        'Base': 'http://10.128.0.1:5000/',
        'Firebase': 'https://surfptz-default-rtdb.firebaseio.com/.json'
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.send_to = 'Base'
        self._latest_latlon = None
    
    def set_dest_addr(self, dest):
        self.send_to = dest
    
    def post_to_base_api(self, endpoint: str):
        url = f'{self.dest_addrs[self.send_to]}{endpoint}'
        print(f'calling {url}')
        requests.post(url=url)
    
    def set_origin(self):
        print(f'setting origin to {self._latest_latlon}')
        requests.post(url=f'{self.dest_addrs[self.send_to]}api/set_origin',
                      data=self._latest_latlon)
    
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

        return Builder.load_file('SurfptzTag.kv')

    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()

    @mainthread
    def on_location(self, **kwargs):
        self.gps_location = '\n'.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])
        self._latest_latlon = {'lat': kwargs['lat'], 'lon': kwargs['lon']}
        # timestamp = datetime.now().isoformat()
        # gps_data = json.dumps({timestamp: kwargs})
        if self.send_to:
            try:
                res = requests.post(
                    url=f'{self.dest_addrs[self.send_to]}api/abscoords',
                    data=self._latest_latlon,
                    params=self._latest_latlon
                )
                print(res.text)
            except:
                print('Failed sending location')

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
