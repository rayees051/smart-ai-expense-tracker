import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 900, 650
FPS = 60

# Colors
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
CYAN        = (0, 220, 255)
DARK_CYAN   = (0, 120, 160)
ORANGE      = (255, 140, 0)
RED         = (220, 50, 50)
YELLOW      = (255, 220, 0)
DARK_BLUE   = (5, 10, 30)
BLUE        = (20, 60, 180)
GRAY        = (160, 160, 180)
DARK_GRAY   = (40, 40, 60)
GREEN       = (50, 220, 80)
PURPLE      = (160, 60, 220)
LIGHT_BLUE  = (100, 180, 255)

# Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("⚡ FIGHTER JET — ACE SQUADRON")
clock = pygame.time.Clock()

# Fonts
try:
    font_large  = pygame.font.SysFont("consolas", 52, bold=True)
    font_medium = pygame.font.SysFont("consolas", 28, bold=True)
    font_small  = pygame.font.SysFont("consolas", 20)
    font_tiny   = pygame.font.SysFont("consolas", 15)
except:
    font_large  = pygame.font.SysFont(None, 52)
    font_medium = pygame.font.SysFont(None, 28)
    font_small  = pygame.font.SysFont(None, 20)
    font_tiny   = pygame.font.SysFont(None, 15)


# ─────────────────────────────────────────────
#  Drawing helpers
# ─────────────────────────────────────────────

def draw_player_jet(surf, x, y, scale=1.0):
    s = scale
    flame_pts = [
        (x,               y + int(38*s)),
        (x - int(8*s),    y + int(56*s)),
        (x,               y + int(48*s)),
        (x + int(8*s),    y + int(56*s)),
    ]
    pygame.draw.polygon(surf, ORANGE, flame_pts)
    inner_flame = [
        (x,               y + int(40*s)),
        (x - int(4*s),    y + int(52*s)),
        (x,               y + int(46*s)),
        (x + int(4*s),    y + int(52*s)),
    ]
    pygame.draw.polygon(surf, YELLOW, inner_flame)

    body = [
        (x,               y - int(36*s)),
        (x + int(10*s),   y - int(10*s)),
        (x + int(12*s),   y + int(20*s)),
        (x,               y + int(36*s)),
        (x - int(12*s),   y + int(20*s)),
        (x - int(10*s),   y - int(10*s)),
    ]
    pygame.draw.polygon(surf, CYAN, body)
    pygame.draw.polygon(surf, WHITE, body, 1)

    left_wing = [
        (x - int(10*s), y),
        (x - int(40*s), y + int(20*s)),
        (x - int(36*s), y + int(30*s)),
        (x - int(12*s), y + int(18*s)),
    ]
    right_wing = [
        (x + int(10*s), y),
        (x + int(40*s), y + int(20*s)),
        (x + int(36*s), y + int(30*s)),
        (x + int(12*s), y + int(18*s)),
    ]
    pygame.draw.polygon(surf, DARK_CYAN, left_wing)
    pygame.draw.polygon(surf, DARK_CYAN, right_wing)
    pygame.draw.polygon(surf, CYAN, left_wing, 1)
    pygame.draw.polygon(surf, CYAN, right_wing, 1)

    pygame.draw.ellipse(surf, LIGHT_BLUE,
                        (x - int(7*s), y - int(30*s), int(14*s), int(20*s)))


def draw_enemy_jet(surf, x, y, color=RED):
    body = [
        (x,           y + 28),
        (x + 9,       y + 8),
        (x + 11,      y - 18),
        (x,           y - 30),
        (x - 11,      y - 18),
        (x - 9,       y + 8),
    ]
    pygame.draw.polygon(surf, color, body)
    pygame.draw.polygon(surf, WHITE, body, 1)

    left_wing = [
        (x - 9,  y),
        (x - 36, y - 14),
        (x - 32, y - 24),
        (x - 11, y - 12),
    ]
    right_wing = [
        (x + 9,  y),
        (x + 36, y - 14),
        (x + 32, y - 24),
        (x + 11, y - 12),
    ]
    dark = tuple(max(0, c - 60) for c in color)
    pygame.draw.polygon(surf, dark, left_wing)
    pygame.draw.polygon(surf, dark, right_wing)
    pygame.draw.polygon(surf, WHITE, left_wing, 1)
    pygame.draw.polygon(surf, WHITE, right_wing, 1)

    pygame.draw.ellipse(surf, (200, 200, 255), (x - 6, y + 12, 12, 16))


# ─────────────────────────────────────────────
#  Stars / background
# ─────────────────────────────────────────────

class Star:
    def __init__(self):
        self.reset(random.randint(0, HEIGHT))

    def reset(self, y=0):
        self.x = random.randint(0, WIDTH)
        self.y = y
        self.speed = random.uniform(1.5, 5)
        self.size  = random.choice([1, 1, 1, 2])
        self.color = random.choice([WHITE, LIGHT_BLUE, CYAN, GRAY])

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.reset()

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)


# ─────────────────────────────────────────────
#  Particles
# ─────────────────────────────────────────────

class Particle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.x  = x
        self.y  = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life  = random.randint(20, 50)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self, surf):
        alpha = self.life / self.max_life
        r = max(0, min(255, int(self.color[0] * alpha)))
        g = max(0, min(255, int(self.color[1] * alpha)))
        b = max(0, min(255, int(self.color[2] * alpha)))
        size = max(1, int(3 * alpha))
        pygame.draw.circle(surf, (r, g, b), (int(self.x), int(self.y)), size)


def explosion(particles, x, y, count=40, color=ORANGE):
    for _ in range(count):
        c = (
            min(255, color[0] + random.randint(-30, 30)),
            min(255, color[1] + random.randint(-30, 30)),
            min(255, color[2] + random.randint(-30, 30)),
        )
        particles.append(Particle(x, y, c))


# ─────────────────────────────────────────────
#  Game objects
# ─────────────────────────────────────────────

class Bullet:
    def __init__(self, x, y, vy=-14, color=CYAN, is_enemy=False):
        self.x = x
        self.y = y
        self.vy = vy
        self.color = color
        self.is_enemy = is_enemy
        self.rect = pygame.Rect(x - 3, y - 8, 6, 16)

    def update(self):
        self.y += self.vy
        self.rect.y = int(self.y) - 8

    def draw(self, surf):
        glow = pygame.Surface((14, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*self.color, 60), (0, 0, 14, 24))
        surf.blit(glow, (int(self.x) - 7, int(self.y) - 12))
        pygame.draw.rect(surf, self.color, (int(self.x) - 3, int(self.y) - 8, 6, 16), border_radius=3)
        pygame.draw.rect(surf, WHITE, (int(self.x) - 1, int(self.y) - 8, 2, 6), border_radius=1)


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = 6
        self.hp = 100
        self.max_hp = 100
        self.shoot_cooldown = 0
        self.shoot_delay = 12
        self.invincible = 0
        self.rect = pygame.Rect(self.x - 14, self.y - 36, 28, 72)
        self.score = 0
        self.shield = 0
        self.triple = 0

    def update(self, keys):
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x += self.speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.y -= self.speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.y += self.speed

        self.x = max(50, min(WIDTH - 50, self.x))
        self.y = max(50, min(HEIGHT - 50, self.y))
        self.rect.center = (int(self.x), int(self.y))

        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if self.invincible > 0:     self.invincible -= 1
        if self.shield > 0:         self.shield -= 1
        if self.triple > 0:         self.triple -= 1

    def shoot(self, bullets):
        if self.shoot_cooldown == 0:
            if self.triple > 0:
                bullets.append(Bullet(self.x - 18, self.y - 20))
                bullets.append(Bullet(self.x,       self.y - 30))
                bullets.append(Bullet(self.x + 18, self.y - 20))
            else:
                bullets.append(Bullet(self.x, self.y - 30))
            self.shoot_cooldown = self.shoot_delay

    def hit(self, dmg=20):
        if self.invincible > 0: return
        if self.shield > 0:
            self.shield = 0
            self.invincible = 60
            return
        self.hp -= dmg
        self.invincible = 45

    def draw(self, surf):
        if self.invincible > 0 and (self.invincible // 5) % 2:
            return
        draw_player_jet(surf, int(self.x), int(self.y))
        if self.shield > 0:
            pygame.draw.circle(surf, CYAN, (int(self.x), int(self.y)), 52, 2)


class Enemy:
    TYPES = {
        "scout":  {"color": RED,    "hp": 20,  "speed": 2.5, "shoot_delay": 90,  "score": 100, "size": 1.0},
        "bomber": {"color": ORANGE, "hp": 60,  "speed": 1.5, "shoot_delay": 60,  "score": 250, "size": 1.3},
        "ace":    {"color": PURPLE, "hp": 100, "speed": 3.5, "shoot_delay": 45,  "score": 500, "size": 1.0},
    }

    def __init__(self, kind="scout"):
        cfg = self.TYPES[kind]
        self.kind  = kind
        self.color = cfg["color"]
        self.hp    = cfg["hp"]
        self.max_hp= cfg["hp"]
        self.speed = cfg["speed"]
        self.shoot_delay = cfg["shoot_delay"]
        self.score = cfg["score"]
        self.size  = cfg["size"]
        self.x = random.randint(60, WIDTH - 60)
        self.y = random.randint(-120, -40)
        self.shoot_cd = random.randint(0, self.shoot_delay)
        self.rect = pygame.Rect(self.x - 12, self.y - 28, 24, 56)
        self.wave_amp    = random.uniform(30, 80)
        self.wave_speed  = random.uniform(0.02, 0.05)
        self.wave_offset = random.uniform(0, math.pi * 2)
        self.base_x = self.x
        self.t = 0
        self.dead = False   # FIX: flag instead of mid-loop removal

    def update(self, bullets):
        self.y += self.speed
        self.t += 1
        self.x = self.base_x + self.wave_amp * math.sin(self.wave_speed * self.t + self.wave_offset)
        self.x = max(50, min(WIDTH - 50, self.x))
        self.rect.center = (int(self.x), int(self.y))

        self.shoot_cd -= 1
        if self.shoot_cd <= 0:
            bullets.append(Bullet(self.x, self.y + 30, vy=7, color=RED, is_enemy=True))
            self.shoot_cd = self.shoot_delay

    def hit(self, dmg=20):
        self.hp -= dmg

    def draw(self, surf):
        draw_enemy_jet(surf, int(self.x), int(self.y), self.color)
        bar_w = 36
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, DARK_GRAY, (int(self.x) - 18, int(self.y) - 40, bar_w, 5))
        pygame.draw.rect(surf, GREEN,     (int(self.x) - 18, int(self.y) - 40, int(bar_w * ratio), 5))


class PowerUp:
    TYPES  = ["health", "shield", "triple", "rapid"]
    COLORS = {"health": GREEN, "shield": CYAN, "triple": YELLOW, "rapid": PURPLE}
    ICONS  = {"health": "+", "shield": "S", "triple": "3", "rapid": "R"}

    def __init__(self):
        self.kind  = random.choice(self.TYPES)
        self.x     = random.randint(60, WIDTH - 60)
        self.y     = -30
        self.speed = 2.5
        self.color = self.COLORS[self.kind]
        self.rect  = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        self.pulse = 0

    def update(self):
        self.y += self.speed
        self.rect.center = (int(self.x), int(self.y))
        self.pulse += 0.1

    def draw(self, surf):
        r = 15 + int(3 * math.sin(self.pulse))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), r)
        pygame.draw.circle(surf, WHITE,      (int(self.x), int(self.y)), r, 2)
        txt = font_small.render(self.ICONS[self.kind], True, BLACK)
        surf.blit(txt, txt.get_rect(center=(int(self.x), int(self.y))))


# ─────────────────────────────────────────────
#  HUD
# ─────────────────────────────────────────────

def draw_hud(surf, player, wave, high_score):
    bar_w = 200
    pygame.draw.rect(surf, DARK_GRAY, (20, 20, bar_w, 18), border_radius=4)
    ratio = max(0, player.hp / player.max_hp)
    col = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
    pygame.draw.rect(surf, col, (20, 20, int(bar_w * ratio), 18), border_radius=4)
    pygame.draw.rect(surf, WHITE, (20, 20, bar_w, 18), 1, border_radius=4)
    hp_txt = font_tiny.render(f"HP  {player.hp}/{player.max_hp}", True, WHITE)
    surf.blit(hp_txt, (228, 22))

    px = 20
    if player.shield > 0:
        s = font_tiny.render(f"SHIELD {player.shield//FPS+1}s", True, CYAN)
        surf.blit(s, (px, 46)); px += s.get_width() + 10
    if player.triple > 0:
        t = font_tiny.render(f"TRIPLE {player.triple//FPS+1}s", True, YELLOW)
        surf.blit(t, (px, 46)); px += t.get_width() + 10

    score_txt = font_medium.render(f"SCORE  {player.score:>7}", True, CYAN)
    surf.blit(score_txt, (WIDTH - score_txt.get_width() - 20, 16))
    wave_txt  = font_small.render(f"WAVE {wave}", True, GRAY)
    surf.blit(wave_txt,  (WIDTH - wave_txt.get_width()  - 20, 50))
    hi_txt    = font_tiny.render(f"BEST  {high_score}", True, GRAY)
    surf.blit(hi_txt,    (WIDTH - hi_txt.get_width()    - 20, 72))

    ctrl = font_tiny.render("ARROWS/WASD move   SPACE shoot", True, DARK_GRAY)
    surf.blit(ctrl, (WIDTH//2 - ctrl.get_width()//2, HEIGHT - 18))


# ─────────────────────────────────────────────
#  Screens
# ─────────────────────────────────────────────

def draw_title_screen(surf, stars):
    surf.fill(DARK_BLUE)
    for s in stars: s.draw(surf)

    title = font_large.render("FIGHTER JET", True, CYAN)
    sub   = font_medium.render("ACE SQUADRON", True, YELLOW)
    start = font_small.render("Press  ENTER  to begin", True, WHITE)
    hint  = font_tiny.render("ARROWS / WASD  move   |   SPACE  shoot", True, GRAY)

    surf.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))
    surf.blit(sub,   sub.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
    surf.blit(start, start.get_rect(center=(WIDTH//2, HEIGHT//2 + 60)))
    surf.blit(hint,  hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 100)))
    draw_player_jet(surf, WIDTH//2, HEIGHT//2 + 200, scale=1.4)
    pygame.display.flip()


def draw_game_over(surf, stars, score, high_score, wave_reached, won=False):
    """Always shows final score, wave reached, and best score."""
    surf.fill(DARK_BLUE)
    for s in stars: s.draw(surf)

    msg   = "MISSION COMPLETE!" if won else "GAME OVER"
    color = YELLOW if won else RED

    t1 = font_large.render(msg, True, color)
    t2 = font_medium.render(f"FINAL SCORE  {score}", True, WHITE)
    t3 = font_small.render(f"WAVE REACHED  {wave_reached}", True, CYAN)
    t4 = font_small.render(f"BEST SCORE   {high_score}", True, GRAY)
    t5 = font_small.render("Press  ENTER  to play again   ESC to quit", True, LIGHT_BLUE)

    surf.blit(t1, t1.get_rect(center=(WIDTH//2, HEIGHT//2 - 110)))
    surf.blit(t2, t2.get_rect(center=(WIDTH//2, HEIGHT//2 - 45)))
    surf.blit(t3, t3.get_rect(center=(WIDTH//2, HEIGHT//2 + 5)))
    surf.blit(t4, t4.get_rect(center=(WIDTH//2, HEIGHT//2 + 45)))
    surf.blit(t5, t5.get_rect(center=(WIDTH//2, HEIGHT//2 + 105)))

    # Decorative jets
    draw_player_jet(surf, WIDTH//2 - 180, HEIGHT//2 + 200, scale=0.9)
    draw_player_jet(surf, WIDTH//2 + 180, HEIGHT//2 + 200, scale=0.9)

    pygame.display.flip()


# ─────────────────────────────────────────────
#  Main game loop
# ─────────────────────────────────────────────

def game():
    stars      = [Star() for _ in range(120)]
    high_score = 0

    while True:
        # ── Title screen ──
        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    waiting = False
            for s in stars: s.update()
            draw_title_screen(screen, stars)
            clock.tick(FPS)

        # ── Play ──
        player       = Player()
        bullets      = []
        enemies      = []
        powerups     = []
        particles    = []
        wave         = 1
        wave_timer   = 0
        spawn_interval = 90
        enemy_count    = 6
        game_over      = False
        won            = False

        while not game_over:
            clock.tick(FPS)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    game_over = True

            keys = pygame.key.get_pressed()
            player.update(keys)
            if keys[pygame.K_SPACE]:
                player.shoot(bullets)

            # ── Spawn enemies ──
            wave_timer += 1
            if wave_timer % spawn_interval == 0 and len(enemies) < enemy_count:
                kind = "scout"
                r = random.random()
                if wave >= 3 and r < 0.25:
                    kind = "ace"
                elif wave >= 2 and r < 0.45:
                    kind = "bomber"
                enemies.append(Enemy(kind))

            # Advance wave
            if wave_timer > 600 * wave:
                wave += 1
                enemy_count    = min(6 + wave * 2, 18)
                spawn_interval = max(30, 90 - wave * 5)
                if wave > 10:
                    won = True
                    game_over = True

            # Spawn power-ups
            if random.random() < 0.003:
                powerups.append(PowerUp())

            # ── Update bullets ──
            bullets_to_remove = set()
            for i, b in enumerate(bullets):
                b.update()
                if b.y < -20 or b.y > HEIGHT + 20:
                    bullets_to_remove.add(i)
            bullets = [b for i, b in enumerate(bullets) if i not in bullets_to_remove]

            # ── Update enemies — collect all changes first ──
            enemies_to_remove  = set()
            bullets_to_remove  = set()

            for ei, e in enumerate(enemies):
                if ei in enemies_to_remove:
                    continue
                e.update(bullets)

                # Flew off bottom
                if e.y > HEIGHT + 60:
                    enemies_to_remove.add(ei)
                    player.hp -= 10
                    continue

                # Hit by player bullet
                for bi, b in enumerate(bullets):
                    if bi in bullets_to_remove:
                        continue
                    if not b.is_enemy and e.rect.collidepoint(b.x, b.y):
                        e.hit(20)
                        bullets_to_remove.add(bi)
                        explosion(particles, int(b.x), int(b.y), 12, ORANGE)
                        if e.hp <= 0:
                            explosion(particles, int(e.x), int(e.y), 50, e.color)
                            player.score += e.score
                            enemies_to_remove.add(ei)
                        break  # one bullet per enemy per frame

            # ── Enemy bullets hit player ──
            for bi, b in enumerate(bullets):
                if bi in bullets_to_remove:
                    continue
                if b.is_enemy and player.rect.collidepoint(b.x, b.y):
                    player.hit(20)
                    bullets_to_remove.add(bi)
                    explosion(particles, int(b.x), int(b.y), 15, RED)

            # ── Direct collision (player vs enemy body) ──
            for ei, e in enumerate(enemies):
                if ei in enemies_to_remove:
                    continue
                if player.rect.colliderect(e.rect):
                    player.hit(30)
                    explosion(particles, int(e.x), int(e.y), 40, ORANGE)
                    enemies_to_remove.add(ei)

            # Apply removals safely
            bullets = [b for i, b in enumerate(bullets) if i not in bullets_to_remove]
            enemies = [e for i, e in enumerate(enemies) if i not in enemies_to_remove]

            # ── Power-ups ──
            powerups_to_remove = set()
            for pi, p in enumerate(powerups):
                p.update()
                if p.y > HEIGHT + 40:
                    powerups_to_remove.add(pi)
                    continue
                if player.rect.collidepoint(p.x, p.y):
                    if   p.kind == "health": player.hp = min(player.max_hp, player.hp + 40)
                    elif p.kind == "shield": player.shield = 300
                    elif p.kind == "triple": player.triple = 300
                    elif p.kind == "rapid":
                        player.shoot_delay = 5
                        player.triple = 180
                    explosion(particles, int(p.x), int(p.y), 20, p.color)
                    powerups_to_remove.add(pi)
            powerups = [p for i, p in enumerate(powerups) if i not in powerups_to_remove]

            # ── Particles ──
            particles = [p for p in particles if p.life > 0]
            for p in particles:
                p.update()

            # ── Check death ──
            if player.hp <= 0:
                player.hp = 0
                game_over = True

            # ── Draw ──
            screen.fill(DARK_BLUE)
            for s in stars:
                s.update()
                s.draw(screen)

            for p in powerups:  p.draw(screen)
            for e in enemies:   e.draw(screen)
            for b in bullets:   b.draw(screen)
            for p in particles: p.draw(screen)
            player.draw(screen)

            draw_hud(screen, player, wave, high_score)
            pygame.display.flip()

        # ── Always show final result screen ──
        high_score = max(high_score, player.score)

        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        waiting = False          # play again
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
            for s in stars: s.update()
            draw_game_over(screen, stars, player.score, high_score, wave, won)
            clock.tick(FPS)


if __name__ == "__main__":
    game()