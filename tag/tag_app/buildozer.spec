[app]
title = SurfptzTagApp
package.name = surfptzTagApps
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = pyproj,python3, kivy, plyer, android, requests, urllib3, chardet, idna, certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.api = 28
[buildozer]
log_level = 2
warn_on_root = 1
