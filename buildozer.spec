[app]

# 앱 기본 정보
title = Space Escape Game
package.name = spaceescapegame
package.domain = com.orion.spaceescapegame

# 소스 코드 경로
source.dir = .
source.include_exts = py,png,jpg,ttf,json,mid,mp3,wav

# 버전 정보
version = 1.0
version.code = 1

# 앱 진입점
source.main = main.py

# 의존성 패키지
requirements = python3,pygame

# 앱 아이콘 (assets/icon.png 파일이 있으면 사용됩니다)
# icon.filename = %(source.dir)s/assets/icon.png

# 스플래시 화면
# presplash.filename = %(source.dir)s/assets/presplash.png

# Android 설정
orientation = landscape
fullscreen = 1

# Android API 레벨
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.ndk_api = 21

# Android 권한
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# Android NDK 빌드 아키텍처 (arm64-v8a: 최신 기기, armeabi-v7a: 구형 기기)
android.archs = arm64-v8a, armeabi-v7a

# 릴리즈 빌드 서명 (Play Store 등록 시 필요)
# android.release_artifact = aab  # Google Play는 AAB 선호
# android.keystore = /path/to/your.keystore
# android.keystore_alias = your_alias
# android.keystore_password = your_password
# android.keyalias_password = your_password

# Pygame for Android 부트스트랩
p4a.bootstrap = sdl2
p4a.branch = master

# 로그 레벨
log_level = 2

[buildozer]
# Buildozer 작업 디렉토리
build_dir = ./.buildozer

# 빌드된 APK/AAB 출력 위치
bin_dir = ./bin

# 경고를 오류로 처리하지 않음
warn_on_root = 1
