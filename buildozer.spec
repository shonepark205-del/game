[app]
title = Space Escape Game
package.name = spaceescapegame
package.domain = com.orion.spaceescapegame

source.dir = .
source.include_exts = py,png,jpg,ttf,json,mid,mp3,wav

version = 1.0
version.code = 1

# ✅ pygame_sdl2 사용 (안드로이드 호환)
requirements = python3,pygame_sdl2

orientation = landscape
fullscreen = 1

android.api = 33
android.minapi = 21

# ✅ NDK 버전을 GitHub Actions 기본값과 맞춤
android.ndk = 27.3.13750724
android.ndk_api = 21

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

p4a.bootstrap = sdl2
p4a.branch = master

log_level = 2

[buildozer]
build_dir = ./.buildozer
bin_dir = ./bin
warn_on_root = 1
