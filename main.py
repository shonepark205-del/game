# ====================================================
# Space Escape Game - Kivy 래퍼 (안드로이드용)
# 원본: pygame / 변환: kivy Canvas + Clock
# ====================================================

import os, sys, json, random, time

os.environ['KIVY_NO_ENV_CONFIG'] = '1'

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line, Triangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics.texture import Texture

# ── 상수 ──────────────────────────────────────
TIME_LIMIT = 30
FPS = 60

# ── 랭킹 파일 경로 ────────────────────────────
try:
    from android.storage import app_storage_path
    RANKING_FILE = os.path.join(app_storage_path(), "ranking.json")
except ImportError:
    RANKING_FILE = "ranking.json"

# ── 랭킹 로드/저장 ────────────────────────────
def load_ranking():
    try:
        if os.path.exists(RANKING_FILE):
            with open(RANKING_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return []

def save_ranking(ranking):
    try:
        with open(RANKING_FILE, "w", encoding="utf-8") as f:
            json.dump(ranking, f, ensure_ascii=False, indent=4)
    except:
        pass

# ── 수학 문제 생성 ────────────────────────────
def generate_math_problem(score=0):
    level = min(3, max(1, (score // 5000) + 1))
    ptype = random.choice(['add','sub','mul','div'])
    if ptype == 'add':
        a, b = random.randint(11*level, 99*level), random.randint(11*level, 99*level)
        return f"{a} + {b} = ?", str(a+b)
    elif ptype == 'sub':
        a, b = random.randint(50*level, 150*level), random.randint(11*level, 49*level)
        return f"{a} - {b} = ?", str(a-b)
    elif ptype == 'mul':
        a, b = random.randint(11*level, 25*level), random.randint(2*level, 9)
        return f"{a} × {b} = ?", str(a*b)
    else:
        b = random.randint(2, 9)
        ans = random.randint(11*level, 30*level)
        return f"{b*ans} ÷ {b} = ?", str(ans)

# ── 아이템 타입 정의 ─────────────────────────
ITEM_DEFS = [
    {"name":"heart",   "color":(1,0.2,0.2,1), "hp":100,  "score":0,    "prob":0.10},
    {"name":"star",    "color":(1,1,0,1),      "hp":0,    "score":100,  "prob":0.35},
    {"name":"diamond", "color":(0,0.5,1,1),    "hp":0,    "score":150,  "prob":0.20},
    {"name":"skull",   "color":(0.5,0.5,0.5,1),"hp":-50,  "score":-500, "prob":0.10},
    {"name":"bomb",    "color":(1,0.3,0,1),    "hp":-100, "score":-200, "prob":0.15},
    {"name":"psh",     "color":(1,0,1,1),      "hp":0,    "score":0,    "prob":0.05},
    {"name":"math",    "color":(0,1,0.5,1),    "hp":0,    "score":0,    "prob":0.05},
]

def get_random_item(w, h, speed_mult=1.0):
    r = random.random()
    total = sum(d["prob"] for d in ITEM_DEFS)
    r *= total
    cum = 0
    for d in ITEM_DEFS:
        cum += d["prob"]
        if r <= cum:
            size = 50
            return {
                "name": d["name"],
                "color": d["color"],
                "hp": d["hp"],
                "score": d["score"],
                "x": random.randint(0, int(w)-size),
                "y": float(h),
                "size": size,
                "speed": random.uniform(3, 7) * speed_mult,
            }
    return get_random_item(w, h, speed_mult)

# ── 텍스트 그리기 헬퍼 ───────────────────────
def draw_label(canvas, text, x, y, font_size=24, color=(1,1,1,1), bold=False):
    lbl = CoreLabel(text=text, font_size=font_size, bold=bold,
                    color=color, font_name="Roboto")
    lbl.refresh()
    tex = lbl.texture
    with canvas:
        Color(*color)
        Rectangle(texture=tex,
                  pos=(x - tex.width//2, y - tex.height//2),
                  size=tex.size)

# ── 메인 게임 위젯 ────────────────────────────
class GameWidget(Widget):
    # 상태
    STATE_START    = -1
    STATE_PLAYING  = 0
    STATE_NAME     = 1
    STATE_RANKING  = 2
    STATE_MATH     = 3
    STATE_MATH_RES = 4

    def __init__(self, **kw):
        super().__init__(**kw)
        self.reset_game()
        Window.bind(on_key_down=self.on_key_down)
        Clock.schedule_interval(self.update, 1/FPS)
        Clock.schedule_interval(self.spawn_item, 0.439)

    def reset_game(self):
        w, h = Window.width, Window.height
        self.state = self.STATE_START
        self.start_screen_time = time.time()
        self.px = w / 2
        self.py = h * 0.15
        self.p_size = 60
        self.hp = 100
        self.score = 0
        self.items = []
        self.ranking = load_ranking()
        self.current_time_limit = TIME_LIMIT
        self.start_time = time.time()
        self.remaining = TIME_LIMIT
        self.dragging = False
        self.input_text = ""
        self.total_score = 0
        self.play_time = 0
        self.invincible = 0
        self.shake = 0
        self.math_problem = ""
        self.math_answer = ""
        self.math_input = ""
        self.math_result_msg = ""
        self.math_result_time = 0
        self.last_score_bonus = 0

    def spawn_item(self, dt):
        if self.state != self.STATE_PLAYING:
            return
        w, h = Window.width, Window.height
        elapsed = time.time() - self.start_time
        speed_mult = 1.0 + (elapsed / 30.0) * 1.5
        self.items.append(get_random_item(w, h, speed_mult))

    def update(self, dt):
        w, h = Window.width, Window.height
        now = time.time()

        if self.state == self.STATE_START:
            if now - self.start_screen_time >= 5.0:
                self.state = self.STATE_PLAYING
                self.start_time = now

        elif self.state == self.STATE_MATH_RES:
            if now - self.math_result_time >= 1.5:
                self.state = self.STATE_PLAYING

        elif self.state == self.STATE_PLAYING:
            if self.invincible > 0:
                self.invincible -= 1
            if self.shake > 0:
                self.shake -= 1

            elapsed = now - self.start_time
            self.remaining = max(0, int(self.current_time_limit - elapsed))

            bonus = self.score // 10000
            if bonus > self.last_score_bonus:
                self.last_score_bonus = bonus
                self.current_time_limit += 5

            for item in self.items[:]:
                item["y"] -= item["speed"]
                # 충돌 검사
                dx = abs(self.px - (item["x"] + item["size"]//2))
                dy = abs(self.py - (item["y"] + item["size"]//2))
                if dx < (self.p_size + item["size"]) // 2 and dy < (self.p_size + item["size"]) // 2:
                    if item["name"] == "psh":
                        self.score += 10000
                        self.current_time_limit += 5
                    elif item["name"] == "math":
                        self.math_problem, self.math_answer = generate_math_problem(self.score)
                        self.math_input = ""
                        self.state = self.STATE_MATH
                    else:
                        if not (self.invincible > 0 and item["hp"] < 0):
                            self.hp += item["hp"]
                            self.score += item["score"]
                            if item["hp"] < 0:
                                self.invincible = 60
                                self.shake = 15
                    self.items.remove(item)
                    continue
                if item["y"] < -item["size"]:
                    self.items.remove(item)

            if self.remaining == 0 or self.hp <= 0:
                self.hp = max(0, self.hp)
                self.total_score = self.hp + self.score
                self.play_time = int(now - self.start_time)
                if len(self.ranking) < 10 or (self.ranking and self.total_score > self.ranking[-1]["score"]) or len(self.ranking) == 0:
                    self.state = self.STATE_NAME
                    self.input_text = ""
                else:
                    self.state = self.STATE_RANKING

        self.draw_scene()

    def draw_scene(self):
        w, h = Window.width, Window.height
        self.canvas.clear()

        ox = random.randint(-6,6) if self.shake > 0 else 0
        oy = random.randint(-6,6) if self.shake > 0 else 0

        with self.canvas:
            # 배경
            Color(0.02, 0.02, 0.1, 1)
            Rectangle(pos=(0,0), size=(w,h))

            # 별 배경
            random.seed(42)
            Color(1,1,1,0.4)
            for _ in range(80):
                sx = random.randint(0, int(w))
                sy = random.randint(0, int(h))
                Ellipse(pos=(sx,sy), size=(2,2))
            random.seed()

        if self.state == self.STATE_START:
            self._draw_start(w, h)
        elif self.state == self.STATE_PLAYING:
            self._draw_playing(w, h, ox, oy)
        elif self.state == self.STATE_MATH:
            self._draw_math(w, h)
        elif self.state == self.STATE_MATH_RES:
            self._draw_math_result(w, h)
        elif self.state == self.STATE_NAME:
            self._draw_name_input(w, h)
        elif self.state == self.STATE_RANKING:
            self._draw_ranking(w, h)

    def _draw_start(self, w, h):
        now = time.time()
        countdown = max(1, 5 - int(now - self.start_screen_time))
        draw_label(self.canvas, "🚀 Space Escape Game", w//2, h*0.82, 32, (0,1,1,1), True)
        draw_label(self.canvas, "-날아라 박시현호-", w//2, h*0.75, 22, (1,0.84,0,1))
        draw_label(self.canvas, f"게임 시작까지: {countdown}초", w//2, h*0.68, 20, (1,1,1,1))

        items_info = [
            ("❤️ 하트 10%", "체력 +100", (1,0.4,0.4,1)),
            ("⭐ 별 35%",  "+100점",   (1,1,0,1)),
            ("💎 다이아 20%","+150점",  (0,0.5,1,1)),
            ("💀 해골 10%", "체력-50, -500점", (0.6,0.6,0.6,1)),
            ("💣 폭탄 15%", "체력-100, -200점",(1,0.4,0,1)),
            ("👤 박시현 5%","+10000점!",  (1,0,1,1)),
            ("🔢 수학 5%",  "정답+5000, 오답-5000",(0,1,0.5,1)),
        ]
        for i, (name, effect, color) in enumerate(items_info):
            draw_label(self.canvas, f"{name}  |  {effect}", w//2, h*0.58 - i*h*0.07, 16, color)

        draw_label(self.canvas, "개발사: 오리온  개발자: 박시현 ver.1", w//2, h*0.04, 14, (0.7,0.7,0.7,1))

    def _draw_item(self, item, ox, oy):
        x, y, size = item["x"]+ox, item["y"]+oy, item["size"]
        name = item["name"]
        with self.canvas:
            Color(*item["color"])
            if name == "star":
                Ellipse(pos=(x, y), size=(size, size))
            elif name == "diamond":
                # 마름모
                Line(points=[x+size//2, y+size, x+size, y+size//2,
                              x+size//2, y,      x, y+size//2, x+size//2, y+size], width=2)
                Color(*(item["color"][:3]), 0.4)
                Triangle(points=[x+size//2, y+size, x+size, y+size//2, x+size//2, y])
                Triangle(points=[x+size//2, y+size, x, y+size//2, x+size//2, y])
            elif name in ("skull","bomb","psh","math"):
                Rectangle(pos=(x,y), size=(size,size))
                draw_label(self.canvas, {"skull":"💀","bomb":"💣","psh":"박시현","math":"수학"}[name],
                           x+size//2, y+size//2, 14, (1,1,1,1))
            else:
                Ellipse(pos=(x, y), size=(size, size))

    def _draw_playing(self, w, h, ox, oy):
        # 아이템
        for item in self.items:
            self._draw_item(item, ox, oy)

        # 플레이어 (우주선 삼각형)
        if self.invincible == 0 or (self.invincible % 10 < 5):
            px, py = self.px + ox, self.py + oy
            s = self.p_size // 2
            with self.canvas:
                Color(0, 1, 1, 1)
                Triangle(points=[px, py+s, px-s, py-s, px+s, py-s])
                Color(1, 0.5, 0, 0.6)
                Triangle(points=[px, py-s, px-s//2, py-s-10, px+s//2, py-s-10])

        # HUD
        hp_color = (0.3,1,0.3,1) if self.hp > 50 else (1,0.3,0.3,1)
        draw_label(self.canvas, f"⏱ {self.remaining}s", w*0.15, h*0.95, 22, (1,1,1,1))
        draw_label(self.canvas, f"❤ {self.hp}", w*0.5, h*0.95, 22, hp_color)
        draw_label(self.canvas, f"⭐ {self.score}", w*0.85, h*0.95, 22, (1,1,0,1))

        # HP 바
        with self.canvas:
            bar_w = w * 0.4
            bx = w*0.3
            by = h*0.91
            Color(0.3,0.3,0.3,1)
            Rectangle(pos=(bx, by), size=(bar_w, 10))
            Color(*hp_color[:3], 1)
            Rectangle(pos=(bx, by), size=(bar_w * min(1, self.hp/100), 10))

    def _draw_math(self, w, h):
        with self.canvas:
            Color(0,0,0,0.7)
            Rectangle(pos=(0,0), size=(w,h))
        draw_label(self.canvas, "🔢 수학 문제!", w//2, h*0.65, 30, (0,1,1,1), True)
        draw_label(self.canvas, self.math_problem,  w//2, h*0.52, 26, (1,1,1,1))
        draw_label(self.canvas, f"답: {self.math_input}_", w//2, h*0.42, 24, (0,1,0,1))
        draw_label(self.canvas, "[엔터=제출  백스페이스=지우기]", w//2, h*0.32, 16, (0.7,0.7,0.7,1))

    def _draw_math_result(self, w, h):
        ok = "정답" in self.math_result_msg
        color = (0.3,1,0.3,1) if ok else (1,0.3,0.3,1)
        draw_label(self.canvas, self.math_result_msg, w//2, h//2, 30, color, True)

    def _draw_name_input(self, w, h):
        with self.canvas:
            Color(0,0,0,0.75)
            Rectangle(pos=(0,0), size=(w,h))
        draw_label(self.canvas, "🏆 랭킹 등록!", w//2, h*0.65, 30, (1,0.84,0,1), True)
        draw_label(self.canvas, f"최종점수: {self.total_score}점", w//2, h*0.55, 22, (1,1,1,1))
        draw_label(self.canvas, "이름 입력 후 엔터:", w//2, h*0.46, 20, (1,1,1,1))
        draw_label(self.canvas, self.input_text + "_", w//2, h*0.37, 24, (0,1,0.5,1))

    def _draw_ranking(self, w, h):
        with self.canvas:
            Color(0,0,0,0.8)
            Rectangle(pos=(0,0), size=(w,h))
        draw_label(self.canvas, "🏆 TOP 10 랭킹", w//2, h*0.9, 30, (1,0.84,0,1), True)
        medals = ["🥇","🥈","🥉"]
        for i, r in enumerate(self.ranking[:10]):
            medal = medals[i] if i < 3 else f"{i+1}."
            color = [(1,0.84,0,1),(0.8,0.8,0.8,1),(0.8,0.5,0.2,1)][i] if i<3 else (0.9,0.9,0.9,1)
            draw_label(self.canvas, f"{medal} {r['name']}  {r['score']}점",
                       w//2, h*0.8 - i*h*0.07, 20, color)
        # 다시하기 버튼
        with self.canvas:
            Color(0,0.7,0,1)
            bw, bh2 = 200, 55
            bx = w//2 - bw//2
            by = h*0.05
            Rectangle(pos=(bx, by), size=(bw, bh2))
        draw_label(self.canvas, "다시하기", w//2, h*0.05+27, 22, (0,0,0,1), True)
        self._restart_rect = (w//2-100, h*0.05, 200, 55)

    # ── 터치/마우스 이벤트 ───────────────────
    def on_touch_down(self, touch):
        w, h = Window.width, Window.height
        if self.state == self.STATE_PLAYING:
            dx = abs(touch.x - self.px)
            dy = abs(touch.y - self.py)
            if dx < self.p_size and dy < self.p_size:
                self.dragging = True
        elif self.state == self.STATE_RANKING:
            rx, ry, rw2, rh2 = self._restart_rect
            if rx <= touch.x <= rx+rw2 and ry <= touch.y <= ry+rh2:
                self.reset_game()

    def on_touch_move(self, touch):
        if self.state == self.STATE_PLAYING and self.dragging:
            w, h = Window.width, Window.height
            self.px = max(self.p_size//2, min(touch.x, w - self.p_size//2))
            self.py = max(self.p_size//2, min(touch.y, h - self.p_size//2))

    def on_touch_up(self, touch):
        self.dragging = False

    # ── 키보드 입력 ──────────────────────────
    def on_key_down(self, window, key, *args):
        from kivy.core.window import Keyboard
        if self.state == self.STATE_MATH:
            if key == Keyboard.keycodes.get('enter', 13) or key == 13:
                if self.math_input == self.math_answer:
                    self.score += 5000
                    self.math_result_msg = "정답입니다! (+5000점)"
                else:
                    self.score -= 5000
                    self.math_result_msg = "틀렸습니다! (-5000점)"
                self.state = self.STATE_MATH_RES
                self.math_result_time = time.time()
            elif key == Keyboard.keycodes.get('backspace', 8) or key == 8:
                self.math_input = self.math_input[:-1]
            elif 48 <= key <= 57:  # 숫자 0-9
                self.math_input += chr(key)
        elif self.state == self.STATE_NAME:
            if key == 13:  # Enter
                name = self.input_text.strip() or "Unknown"
                self.ranking.append({"name": name, "score": self.total_score, "time": self.play_time})
                self.ranking.sort(key=lambda x: x["score"], reverse=True)
                self.ranking = self.ranking[:10]
                save_ranking(self.ranking)
                self.state = self.STATE_RANKING
            elif key == 8:  # Backspace
                self.input_text = self.input_text[:-1]
            elif 32 <= key <= 126:
                self.input_text += chr(key)

# ── 앱 ───────────────────────────────────────
class SpaceEscapeApp(App):
    def build(self):
        self.title = "Space Escape Game"
        return GameWidget()

if __name__ == "__main__":
    SpaceEscapeApp().run()
