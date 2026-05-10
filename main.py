import pygame
import random
import time
import os
import sys
import json

# Android detection
try:
    import android
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

# Initialize Pygame
pygame.init()

# Constants - Use full screen on Android
if IS_ANDROID:
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
else:
    WIDTH = 800
    HEIGHT = 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

FPS = 60
TIME_LIMIT = 30 # seconds

# Scale factor for UI elements
SCALE = min(WIDTH / 800, HEIGHT / 600)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

pygame.display.set_caption("Space Escape Game")
clock = pygame.time.Clock()

# Fonts - Use bundled font on Android
def get_font(size, bold=False):
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "NanumGothic.ttf")
    if os.path.exists(font_path):
        return pygame.font.Font(font_path, int(size * SCALE))
    # Fallback
    for name in ["malgungothic", "nanumgothic", "unifont", None]:
        try:
            return pygame.font.SysFont(name, int(size * SCALE), bold=bold)
        except:
            continue
    return pygame.font.Font(None, int(size * SCALE))

font = get_font(32)
large_font = get_font(48, bold=True)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Ranking file path (writable on Android)
if IS_ANDROID:
    from android.storage import app_storage_path
    RANKING_FILE = os.path.join(app_storage_path(), "ranking.json")
else:
    RANKING_FILE = "ranking.json"

# Load Assets safely
def load_image(name, scale_size):
    try:
        path = os.path.join(ASSETS_DIR, name)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, scale_size)
    except Exception as e:
        # Fallback if image doesn't exist
        print(f"Warning: Could not load {name}, using fallback shape.")
        surface = pygame.Surface(scale_size, pygame.SRCALPHA)
        if name == "spaceship.png":
            pygame.draw.polygon(surface, (0, 255, 255), [(scale_size[0]//2, 0), (0, scale_size[1]), (scale_size[0], scale_size[1])])
        elif name == "heart.png":
            pygame.draw.circle(surface, RED, (scale_size[0]//2, scale_size[1]//2), scale_size[0]//2)
        elif name == "star.png":
            pygame.draw.circle(surface, (255, 255, 0), (scale_size[0]//2, scale_size[1]//2), scale_size[0]//2)
        elif name == "diamond.png":
            pygame.draw.polygon(surface, (0, 0, 255), [(scale_size[0]//2, 0), (0, scale_size[1]//2), (scale_size[0]//2, scale_size[1]), (scale_size[0], scale_size[1]//2)])
        elif name == "skull.png":
            font_small = pygame.font.SysFont("malgungothic", 16, bold=True)
            text = font_small.render("해골", True, WHITE)
            surface.blit(text, (scale_size[0]//2 - text.get_width()//2, scale_size[1]//2 - text.get_height()//2))
        elif name == "bomb.png":
            font_small = pygame.font.SysFont("malgungothic", 16, bold=True)
            text = font_small.render("폭탄", True, RED)
            surface.blit(text, (scale_size[0]//2 - text.get_width()//2, scale_size[1]//2 - text.get_height()//2))
        elif name == "psh.png":
            font_small = pygame.font.SysFont("malgungothic", 16, bold=True)
            text = font_small.render("박시현", True, (255, 0, 255))
            surface.blit(text, (scale_size[0]//2 - text.get_width()//2, scale_size[1]//2 - text.get_height()//2))
        elif name == "math.png":
            font_small = pygame.font.SysFont("malgungothic", 16, bold=True)
            text = font_small.render("수학", True, GREEN)
            surface.blit(text, (scale_size[0]//2 - text.get_width()//2, scale_size[1]//2 - text.get_height()//2))
        return surface

spaceship_img = load_image("spaceship.png", (64, 64))
heart_img = load_image("heart.png", (40, 40))
star_img = load_image("star.png", (40, 40))
diamond_img = load_image("diamond.png", (40, 40))
skull_img = load_image("skull.png", (40, 40))
bomb_img = load_image("bomb.png", (40, 40))
psh_img = load_image("psh.png", (60, 60))
math_img = load_image("math.png", (40, 40))

try:
    bg_img = pygame.image.load(os.path.join(ASSETS_DIR, "spaceship_bg.jpg")).convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
except Exception as e:
    bg_img = None

ITEM_TYPES = [
    {"name": "heart", "image": heart_img, "hp": 100, "score": 0, "prob": 0.10},
    {"name": "star", "image": star_img, "hp": 0, "score": 100, "prob": 0.35},
    {"name": "diamond", "image": diamond_img, "hp": 0, "score": 150, "prob": 0.20},
    {"name": "skull", "image": skull_img, "hp": -50, "score": -500, "prob": 0.10},
    {"name": "bomb", "image": bomb_img, "hp": -100, "score": -200, "prob": 0.15},
    {"name": "psh", "image": psh_img, "hp": 0, "score": 0, "prob": 0.05},
    {"name": "math", "image": math_img, "hp": 0, "score": 0, "prob": 0.05},
]

def load_ranking():
    if os.path.exists(RANKING_FILE):
        try:
            with open(RANKING_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_ranking(ranking):
    with open(RANKING_FILE, "w", encoding="utf-8") as f:
        json.dump(ranking, f, ensure_ascii=False, indent=4)

def generate_math_problem(score=0):
    level = min(3, max(1, (score // 5000) + 1))
    problem_types = ['add', 'sub', 'mul', 'div', 'div_decimal', 'unit_km_m', 'unit_cm_mm', 'area_rect', 'percentage', 'sequence']
    ptype = random.choice(problem_types)
    
    if ptype == 'add':
        a = random.randint(11 * level, 99 * level)
        b = random.randint(11 * level, 99 * level)
        ans = a + b
        return f"{a} + {b} = ?", str(ans)
    elif ptype == 'sub':
        a = random.randint(50 * level, 150 * level)
        b = random.randint(11 * level, 49 * level)
        ans = a - b
        return f"{a} - {b} = ?", str(ans)
    elif ptype == 'mul':
        a = random.randint(11 * level, 25 * level)
        b = random.randint(2 * level, 9)
        ans = a * b
        return f"{a} × {b} = ?", str(ans)
    elif ptype == 'div':
        b = random.randint(2, 9)
        ans = random.randint(11 * level, 30 * level)
        a = b * ans
        return f"{a} ÷ {b} = ?", str(ans)
    elif ptype == 'div_decimal':
        b = random.choice([2, 4, 5, 8, 10])
        a = random.randint(11, 30)
        ans = a / b
        ans_str = str(int(ans)) if ans.is_integer() else str(ans)
        return f"{a} ÷ {b} = ?", ans_str
    elif ptype == 'unit_km_m':
        km = random.randint(2 * level, 9 * level)
        return f"{km}km는 몇 m입니까?", str(km * 1000)
    elif ptype == 'unit_cm_mm':
        cm = random.randint(5 * level, 20 * level)
        return f"{cm}cm는 몇 mm입니까?", str(cm * 10)
    elif ptype == 'area_rect':
        w = random.randint(5 * level, 15 * level)
        h = random.randint(4 * level, 10 * level)
        return f"가로 {w}, 세로 {h} 직사각형 넓이는?", str(w * h)
    elif ptype == 'percentage':
        base = random.choice([50, 100, 200, 300, 400, 500]) * level
        percent = random.choice([10, 20, 25, 50])
        ans = base * percent // 100
        return f"{base}의 {percent}%는 얼마입니까?", str(ans)
    elif ptype == 'sequence':
        start = random.randint(2 * level, 10 * level)
        step = random.randint(2 * level, 5 * level)
        seq = [start + step * i for i in range(4)]
        return f"{seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ?에 올 수는?", str(start + step * 4)

class Player:
    def __init__(self):
        self.image = spaceship_img
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 100)
        self.hp = 100
        self.score = 0
        self.dragging = False

    def draw(self, surface, offset_x=0, offset_y=0):
        surface.blit(self.image, (self.rect.x + offset_x, self.rect.y + offset_y))

class FallingItem:
    def __init__(self, item_info, speed_multiplier=1.0):
        self.info = item_info
        self.image = item_info["image"]
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.y = -50.0
        self.rect.y = int(self.y)
        self.speed = random.randint(3, 7) * 0.945 * speed_multiplier # Reduced by 10% (1.05 * 0.9)
        self.spawn_time = time.time()

    def update(self):
        self.y += self.speed
        self.rect.y = int(self.y)

    def draw(self, surface, offset_x=0, offset_y=0):
        surface.blit(self.image, (self.rect.x + offset_x, self.rect.y + offset_y))

def get_random_item(speed_multiplier=1.0, elapsed_time=0):
    is_skull_time = False
    if elapsed_time > 0 and int(elapsed_time) % 15 == 0:
        is_skull_time = True

    probs = []
    for item in ITEM_TYPES:
        p = item["prob"]
        if is_skull_time:
            if item["name"] == "skull":
                p = 0.50
            else:
                p = (item["prob"] / 0.90) * 0.50
        probs.append((item, p))
        
    total_prob = sum(p for _, p in probs)
    r = random.uniform(0, total_prob)
    cumulative = 0
    for item, p in probs:
        cumulative += p
        if r <= cumulative:
            return FallingItem(item, speed_multiplier)
    return FallingItem(ITEM_TYPES[1], speed_multiplier) # default star

def main():
    # Load Music
    music_loaded = False
    music_files = []
    for ext in ['.mid', '.mp3', '.wav']:
        for base in ['midi', 'midi2']:
            music_path = os.path.join(ASSETS_DIR, f"{base}{ext}")
            if os.path.exists(music_path):
                music_files.append(music_path)
    
    MUSIC_END = pygame.USEREVENT + 2
    pygame.mixer.music.set_endevent(MUSIC_END)
    current_music_index = 0
            
    if music_files:
        try:
            pygame.mixer.music.load(music_files[current_music_index])
            pygame.mixer.music.play()
            music_loaded = True
        except:
            pass
    if not music_loaded:
        print("Warning: Could not load midi background music.")

    player = Player()
    items = []
    
    current_time_limit = TIME_LIMIT
    start_time = time.time()
    
    # Game States
    STATE_START = -1
    STATE_PLAYING = 0
    STATE_NAME_INPUT = 1
    STATE_RANKING = 2
    STATE_MATH = 3
    STATE_MATH_RESULT = 4
    state = STATE_START
    start_screen_timer = time.time()
    
    # Variables for Name Input
    input_text = ""
    composition_text = ""
    ranking = load_ranking()
    total_score = 0
    play_time = 0
    
    # Variables for Math Problem
    math_problem = ""
    math_answer = ""
    math_input = ""
    math_start_time = 0
    math_result_msg = ""
    math_result_timer = 0
    
    # Variables for FX and Mechanics
    shake_timer = 0
    invincible_timer = 0
    last_score_bonus = 0
    last_music_period = 0
    
    # Custom event for spawning items
    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 439) # Spawn every ~0.439s (+3% frequency again)

    running = True
    while running:
        current_time = time.time()
        
        if state == STATE_START:
            if current_time - start_screen_timer >= 5.0:
                state = STATE_PLAYING
                start_time = time.time()
                
        if state == STATE_MATH_RESULT:
            if current_time - math_result_timer >= 1.5:
                start_time += (current_time - math_start_time)
                state = STATE_PLAYING
                
        if state == STATE_PLAYING:
            if invincible_timer > 0:
                invincible_timer -= 1
            if shake_timer > 0:
                shake_timer -= 1
                
            if player.score // 10000 > last_score_bonus:
                last_score_bonus = player.score // 10000
                current_time_limit += 5
                
            elapsed_time = current_time - start_time
            remaining_time = max(0, int(current_time_limit - elapsed_time))
            
            current_music_period = int(elapsed_time) // 20
            if current_music_period > last_music_period:
                last_music_period = current_music_period
                if music_files:
                    current_music_index = (current_music_index + 1) % len(music_files)
                    try:
                        pygame.mixer.music.load(music_files[current_music_index])
                        pygame.mixer.music.play()
                    except:
                        pass

            if remaining_time == 0 or player.hp <= 0:
                total_score = max(0, player.hp) + player.score
                play_time = int(elapsed_time)
                if len(ranking) < 10 or total_score > ranking[-1]["score"]:
                    state = STATE_NAME_INPUT
                    pygame.key.start_text_input()
                else:
                    state = STATE_RANKING

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == MUSIC_END:
                if music_files:
                    current_music_index = (current_music_index + 1) % len(music_files)
                    try:
                        pygame.mixer.music.load(music_files[current_music_index])
                        pygame.mixer.music.play()
                    except:
                        pass
            
            if state == STATE_PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                    if event.type == pygame.FINGERDOWN:
                        pos = (int(event.x * WIDTH), int(event.y * HEIGHT))
                    else:
                        pos = event.pos
                    if player.rect.collidepoint(pos):
                        player.dragging = True
                
                elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP:
                    player.dragging = False
                
                elif event.type == pygame.MOUSEMOTION or event.type == pygame.FINGERMOTION:
                    if player.dragging:
                        if event.type == pygame.FINGERMOTION:
                            pos = (int(event.x * WIDTH), int(event.y * HEIGHT))
                        else:
                            pos = event.pos
                        # Move player with touch/mouse but keep centered
                        player.rect.center = pos
                        # Clamp to screen
                        player.rect.x = max(0, min(player.rect.x, WIDTH - player.rect.width))
                        player.rect.y = max(0, min(player.rect.y, HEIGHT - player.rect.height))

                elif event.type == SPAWN_EVENT:
                    speed_mult = 1.0 + (elapsed_time / 30.0) * 1.5 if state == STATE_PLAYING else 1.0
                    items.append(get_random_item(speed_mult, elapsed_time if state == STATE_PLAYING else 0))

            elif state == STATE_MATH:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if math_input == math_answer:
                            player.score += 5000
                            math_result_msg = "정답입니다! (+5000점)"
                        else:
                            player.score -= 5000
                            math_result_msg = "틀렸습니다! (-5000점)"
                        state = STATE_MATH_RESULT
                        math_result_timer = time.time()
                        math_input = ""
                        pygame.key.stop_text_input()
                    elif event.key == pygame.K_BACKSPACE:
                        math_input = math_input[:-1]
                elif event.type == pygame.TEXTINPUT:
                    if event.text.isdigit() or event.text in ['-', '.']:
                        if len(math_input) < 10:
                            math_input += event.text
            
            elif state == STATE_NAME_INPUT:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.key.stop_text_input()
                        final_name = input_text + composition_text
                        if not final_name.strip():
                            final_name = "Unknown"
                        ranking.append({"name": final_name, "score": total_score, "time": play_time})
                        ranking.sort(key=lambda x: x["score"], reverse=True)
                        ranking = ranking[:10]
                        save_ranking(ranking)
                        state = STATE_RANKING
                    elif event.key == pygame.K_BACKSPACE:
                        if len(composition_text) == 0 and len(input_text) > 0:
                            input_text = input_text[:-1]
                elif event.type == pygame.TEXTINPUT:
                    if len(input_text) < 15:
                        input_text += event.text
                        input_text = input_text[:15]
                    composition_text = ""
                elif event.type == pygame.TEXTEDITING:
                    if len(input_text) + len(event.text) <= 15:
                        composition_text = event.text
                    else:
                        composition_text = event.text[:15 - len(input_text)]
            
            elif state == STATE_RANKING:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check individual delete buttons
                    clicked_delete = False
                    for i in range(len(ranking)):
                        delete_rect = pygame.Rect(WIDTH - 100, 130 + i * 40, 30, 30)
                        if delete_rect.collidepoint(event.pos):
                            ranking.pop(i)
                            save_ranking(ranking)
                            clicked_delete = True
                            break
                    if clicked_delete:
                        continue
                        
                    restart_rect = pygame.Rect(WIDTH//2 - 75, HEIGHT - 80, 150, 50)
                    
                    if restart_rect.collidepoint(event.pos):
                        # Restart game
                        player = Player()
                        items.clear()
                        current_time_limit = TIME_LIMIT
                        state = STATE_START
                        start_screen_timer = time.time()
                        input_text = ""
                        composition_text = ""

        if state == STATE_PLAYING:
            # Update items
            for item in items[:]:
                item.update()
                
                # Check collision
                if player.rect.colliderect(item.rect):
                    if invincible_timer > 0 and item.info["hp"] < 0:
                        pass # Ignore damage items while invincible
                    elif item.info["name"] == "psh":
                        player.score += 10000
                        items.remove(item)
                    elif item.info["name"] == "math":
                        math_problem, math_answer = generate_math_problem(player.score)
                        math_input = ""
                        math_start_time = time.time()
                        pygame.key.start_text_input()
                        state = STATE_MATH
                        items.remove(item)
                    else:
                        player.hp += item.info["hp"]
                        player.score += item.info["score"]
                        if item.info["hp"] < 0:
                            invincible_timer = 60
                            shake_timer = 15
                        items.remove(item)
                    continue
                
                # Remove if off screen
                if item.rect.y > HEIGHT:
                    items.remove(item)

        # Drawing
        offset_x, offset_y = 0, 0
        if state == STATE_PLAYING and shake_timer > 0:
            offset_x = random.randint(-8, 8)
            offset_y = random.randint(-8, 8)

        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(BLACK)

        if state == STATE_START:
            title_text = large_font.render("Space Game Asset Version", True, (0, 255, 255))
            subtitle_text = font.render("-날아라 박시현호-", True, (255, 215, 0))
            countdown = max(1, 5 - int(current_time - start_screen_timer))
            countdown_text = font.render(f"게임 시작까지: {countdown}초", True, WHITE)
            
            font_small = pygame.font.SysFont("malgungothic", 20)
            dev_text = font_small.render("개발사: 오리온, 개발자: 박시현 2026.05.09 ver.1", True, (200, 200, 200))
            
            # Shift title up
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
            screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, 80))
            screen.blit(countdown_text, (WIDTH//2 - countdown_text.get_width()//2, 120))
            
            # Draw Item Table
            korean_names = {
                "heart": "하트",
                "star": "별",
                "diamond": "다이아몬드",
                "skull": "해골",
                "bomb": "폭탄",
                "psh": "박시현(보너스)",
                "math": "수학문제"
            }
            
            for idx, item in enumerate(ITEM_TYPES):
                pct = int(item["prob"] * 100)
                
                if item["name"] == "psh":
                    score_str = "점수: 10000, 시간: +5초"
                elif item["name"] == "math":
                    score_str = "정답: +5000, 오답: -5000"
                else:
                    score_str = f"점수: {item['score']}"
                    if item["hp"] != 0:
                        score_str += f", 체력: {item['hp']}"
                
                kor_name = korean_names.get(item["name"], item["name"].upper())
                info_str = f"{kor_name} - {pct}% | {score_str}"
                info_text = font_small.render(info_str, True, WHITE)
                
                # Draw icon and text
                item_img = pygame.transform.scale(item["image"], (30, 30))
                screen.blit(item_img, (WIDTH//2 - 250, 180 + idx * 40))
                screen.blit(info_text, (WIDTH//2 - 200, 180 + idx * 40 + 5))
                
            screen.blit(dev_text, (WIDTH - dev_text.get_width() - 10, HEIGHT - dev_text.get_height() - 10))

        elif state == STATE_PLAYING:
            if invincible_timer == 0 or (invincible_timer % 10 < 5):
                player.draw(screen, offset_x, offset_y)
            for item in items:
                item.draw(screen, offset_x, offset_y)

            # Draw HUD
            hud_text = f"Time: {remaining_time}s   HP: {player.hp}   Score: {player.score}"
            text_surface = font.render(hud_text, True, WHITE)
            screen.blit(text_surface, (10 + offset_x, 10 + offset_y))
            
        elif state == STATE_MATH_RESULT:
            color = GREEN if "정답" in math_result_msg else RED
            res_text = large_font.render(math_result_msg, True, color)
            screen.blit(res_text, (WIDTH//2 - res_text.get_width()//2, HEIGHT//2 - res_text.get_height()//2))
            
        elif state == STATE_MATH:
            title_text = large_font.render("수학 문제!", True, (0, 255, 255))
            desc_text = font.render(f"문제: {math_problem}", True, WHITE)
            input_surface = font.render(f"정답 입력: {math_input}", True, GREEN)
            
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 100))
            screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, HEIGHT//2 - 30))
            screen.blit(input_surface, (WIDTH//2 - input_surface.get_width()//2, HEIGHT//2 + 20))
            
        elif state == STATE_NAME_INPUT:
            title_text = large_font.render("랭킹 등록!", True, (255, 215, 0))
            desc_text = font.render("이름을 입력하세요 (엔터로 완료):", True, WHITE)
            name_text = font.render(input_text + composition_text, True, GREEN)
            
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 100))
            screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, HEIGHT//2 - 30))
            screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, HEIGHT//2 + 20))
            
        elif state == STATE_RANKING:
            title_text = large_font.render("TOP 10 랭킹", True, (255, 215, 0))
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
            
            for i, rank in enumerate(ranking):
                time_val = rank.get('time', 0)
                rank_text = font.render(f"{i+1}. {rank['name']} - {rank['score']}점 ({time_val}초)", True, WHITE)
                screen.blit(rank_text, (50, 130 + i * 40))
                
                # Draw individual delete button
                delete_rect = pygame.Rect(WIDTH - 100, 130 + i * 40, 30, 30)
                pygame.draw.rect(screen, RED, delete_rect)
                del_text = font.render("X", True, WHITE)
                screen.blit(del_text, (delete_rect.centerx - del_text.get_width()//2, delete_rect.centery - del_text.get_height()//2))
                
            # Restart Button
            restart_rect = pygame.Rect(WIDTH//2 - 75, HEIGHT - 80, 150, 50)
            pygame.draw.rect(screen, GREEN, restart_rect)
            restart_text = font.render("다시하기", True, BLACK)
            screen.blit(restart_text, (restart_rect.centerx - restart_text.get_width()//2, restart_rect.centery - restart_text.get_height()//2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
