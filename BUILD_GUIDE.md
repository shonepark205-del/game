# 🚀 Space Escape Game - 안드로이드 APK 빌드 가이드

**개발자:** 박시현 / 오리온  
**버전:** 1.0 (2026.05.09)  
**목표:** Python/Pygame 게임 → 안드로이드 APK → 구글 플레이스토어 출시

---

## 📋 전체 흐름 요약

```
소스코드 준비 → Ubuntu 환경 구성 → Buildozer 설치 → APK 빌드 → 서명 → 플레이스토어 업로드
```

---

## 1단계: 프로젝트 파일 준비

### 필수 파일 구조
```
space_game_android/
├── main.py              ✅ (제공됨 - 안드로이드 수정 완료)
├── buildozer.spec       ✅ (제공됨)
├── assets/
│   ├── NanumGothic.ttf  ⚠️ 반드시 추가 필요 (한글 폰트)
│   ├── icon.png         ⚠️ 추가 권장 (512x512 앱 아이콘)
│   ├── presplash.png    ⚠️ 추가 권장 (스플래시 화면)
│   ├── spaceship.png    (선택 - 없으면 폴백 도형 사용)
│   ├── heart.png        (선택)
│   ├── star.png         (선택)
│   ├── diamond.png      (선택)
│   ├── skull.png        (선택)
│   ├── bomb.png         (선택)
│   ├── psh.png          (선택)
│   ├── math.png         (선택)
│   └── spaceship_bg.jpg (선택)
└── bin/                 (빌드 후 APK 생성됨)
```

### 한글 폰트 다운로드 (NanumGothic.ttf)
```bash
# 방법 1: wget으로 다운로드
wget -O assets/NanumGothic.ttf \
  "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"

# 방법 2: 구글 폰트에서 직접 다운로드
# https://fonts.google.com/specimen/Nanum+Gothic
# 다운받은 후 assets/ 폴더에 NanumGothic.ttf 이름으로 저장
```

---

## 2단계: 빌드 환경 구성 (Ubuntu 22.04 LTS 권장)

> ⚠️ **Windows 사용자**: WSL2(Windows Subsystem for Linux)를 사용하거나,
> 아래 Docker 방법을 사용하세요.

### 방법 A: 직접 Ubuntu에서 빌드

```bash
# 1. 시스템 패키지 업데이트
sudo apt update && sudo apt upgrade -y

# 2. 필수 패키지 설치
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    build-essential \
    ccache

# 3. Java 환경변수 설정
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
source ~/.bashrc

# 4. Buildozer 설치
pip3 install --user buildozer
pip3 install --user cython==0.29.36

# 5. PATH 추가
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

### 방법 B: Docker로 빌드 (권장 - 환경 문제 없음)

```bash
# Docker 설치 후 실행
docker pull kivy/buildozer

# 프로젝트 폴더에서 실행
docker run --volume "$(pwd)":/home/user/hostcwd \
           kivy/buildozer \
           android debug
```

---

## 3단계: APK 빌드

```bash
# 프로젝트 폴더로 이동
cd space_game_android/

# 디버그 APK 빌드 (처음 빌드는 30분~1시간 소요)
buildozer android debug

# 빌드 완료 후 APK 위치:
# ./bin/spaceescapegame-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

### 빌드 중 오류 대처
```bash
# NDK 오류 시
buildozer android clean
buildozer android debug 2>&1 | tee build.log  # 로그 저장

# 캐시 초기화
rm -rf .buildozer/
buildozer android debug
```

---

## 4단계: 기기에서 테스트

```bash
# USB 디버깅 켠 안드로이드 기기 연결 후
buildozer android deploy run

# 또는 ADB로 직접 설치
adb install bin/spaceescapegame-1.0-*-debug.apk
```

---

## 5단계: 릴리즈 APK 서명 (플레이스토어 업로드용)

### 5-1. 키스토어 생성 (최초 1회)
```bash
keytool -genkey -v \
  -keystore my-release-key.keystore \
  -alias space-game-alias \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# 입력 항목:
# 키스토어 암호: (기억할 암호 입력)
# 이름/조직/도시 등: 입력
```

⚠️ **중요**: 키스토어 파일을 절대 분실하지 마세요! 앱 업데이트 시 동일 키가 필요합니다.

### 5-2. buildozer.spec에 서명 정보 추가
`buildozer.spec` 파일에서 아래 주석 해제 후 값 입력:
```ini
android.release_artifact = aab
android.keystore = /절대경로/my-release-key.keystore
android.keystore_alias = space-game-alias
android.keystore_password = 암호입력
android.keyalias_password = 암호입력
```

### 5-3. 릴리즈 빌드
```bash
buildozer android release
# 결과: ./bin/spaceescapegame-1.0-*-release.aab
```

---

## 6단계: 구글 플레이스토어 등록

### 사전 준비물
| 항목 | 내용 |
|------|------|
| 개발자 계정 | https://play.google.com/console (1회 $25 등록비) |
| 앱 아이콘 | 512×512 PNG |
| 스크린샷 | 최소 2장 (폰: 16:9, 태블릿 선택) |
| 앱 설명 | 한글/영어 짧은 설명 + 긴 설명 |
| 개인정보처리방침 URL | 앱에 개인정보 수집 없어도 필요 |
| AAB 파일 | 릴리즈 빌드 결과물 |

### 등록 절차
1. https://play.google.com/console 접속 → 앱 만들기
2. 앱 정보 입력 (이름: Space Escape Game, 언어: 한국어)
3. **앱 콘텐츠** → 앱 액세스 권한, 개인정보 설정
4. **제작** → 프로덕션 → 새 릴리즈 → AAB 업로드
5. 검토 제출 (보통 1~7일 심사)

---

## 🔧 안드로이드 최적화 사항 (이미 적용됨)

| 항목 | 변경 내용 |
|------|----------|
| 화면 크기 | 기기 해상도 자동 감지 (전체화면) |
| 터치 지원 | FINGERDOWN/FINGERUP/FINGERMOTION 이벤트 추가 |
| 한글 폰트 | NanumGothic.ttf 번들 폰트 사용 |
| 파일 경로 | 앱 내부 저장소 자동 사용 (ranking.json) |
| UI 스케일 | 해상도에 따라 폰트/UI 자동 조절 |

---

## ❓ 자주 묻는 질문

**Q: Windows에서 빌드할 수 없나요?**  
A: Buildozer는 Linux 전용입니다. WSL2(Ubuntu) 또는 Docker를 사용하세요.

**Q: 첫 빌드가 너무 오래 걸려요**  
A: Android NDK/SDK를 처음 다운로드하므로 30분~1시간이 정상입니다.

**Q: 구글 플레이 말고 바로 APK를 배포할 수 있나요?**  
A: 가능합니다. `debug.apk` 또는 서명된 `release.apk`를 직접 배포하면 됩니다.  
단, 기기에서 "출처를 알 수 없는 앱 설치"를 허용해야 합니다.

---

## 📞 참고 링크

- Buildozer 공식 문서: https://buildozer.readthedocs.io
- pygame-ce 안드로이드: https://github.com/pygame-community/pygame-ce
- 구글 플레이 콘솔: https://play.google.com/console
- Nanum 폰트: https://fonts.google.com/specimen/Nanum+Gothic
