[app]
title = Space Escape Game
package.name = spaceescapegame
package.domain = com.orion.spaceescapegame

source.dir = .
source.include_exts = py,png,jpg,ttf,json,mid,mp3,wav

version = 1.0
version.code = 1

requirements = python3,pygame

orientation = landscape
fullscreen = 1

# ✅ 안정적인 버전으로 낮춤 (37 → 33)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# ✅ build tools 명시적으로 낮은 버전 지정
android.sdk = 33
android.build_tools_version = 33.0.2

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.archs = arm64-v8a, armeabi-v7a

# ✅ 라이선스 자동 동의
android.accept_sdk_license = True

p4a.bootstrap = sdl2
p4a.branch = master

log_level = 2

[buildozer]
build_dir = ./.buildozer
bin_dir = ./bin
warn_on_root = 1
