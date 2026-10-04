[app]
title = BRO'S LED Controller
package.name = brosled
package.domain = com.brosengineering
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,md,mp4
version = 1.0
requirements = python3,kivy==2.3.0,Pillow,ffpyplayer
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,CHANGE_WIFI_MULTICAST_STATE
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.arch = arm64-v8a
android.allow_backup = True
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
