import pygame
import math
import sys
import random

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
FPS = 60

# Colors (RGB)
BG_COLOR = (26, 26, 29)
PLAYER_COLOR = (52, 152, 219)
PLAYER_DARK = (41, 128, 185)
ENEMY_COLOR = (231, 76, 60)
OUTLINE_COLOR = (15, 15, 15)
EYE_COLOR = (255, 255, 255)
PUPIL_COLOR = (0, 0, 0)
SWORD_BLADE = (236, 240, 241)
SWORD_GUARD = (241, 196, 15)
ARC_COLOR = (241, 196, 15)
TEXT_COLOR = (240, 240, 240)
HEALTH_BAR_BG = (60, 20, 20)
HEALTH_BAR_FILL = (46, 204, 113)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 22
        self.speed = 4.0
        self.facing_angle = 0.0
        self.max_hp = 500
        self.hp = self.max_hp
        
        # Combat parameters
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 10  # Speed of swing animation
        self.attack_range = 85
        self.hit_enemies_this_swing = set() # Track hits per swing

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1

        # Normalize speed for diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Keep inside screen boundaries
        self.x = max(self.radius + 10, min(SCREEN_WIDTH - self.radius - 10, self.x))
        self.y = max(self.radius + 10, min(SCREEN_HEIGHT - self.radius - 10, self.y))

        # Track mouse rotation
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.facing_angle = math.atan2(mouse_y - self.y, mouse_x - self.x)

        # Trigger attack on click
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.hit_enemies_this_swing.clear()

    def update(self):
        if self.is_attacking:
            self.attack_timer -= 1
            if self.attack_timer  0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, OUTLINE_COLOR, (int(self.x), int(self.y)), self.radius + 2)
        pygame.draw.circle(surface, ENEMY_COLOR, (int(self.x), int(self.y)), self.radius)


class GameController:
    def __init__(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.wave = 0
        self.score = 0
        self.state = "RUNNING" # RUNNING or GAME_OVER
        self.start_next_wave()

    def start_next_wave(self):
        self.wave += 1
        # Determine wave count scaling (e.g. Wave 1 = 5, Wave 2 = 10, etc.)
        num_enemies = self.wave * 5
        
        for _ in range(num_enemies):
            # Spawn enemies outside the screen borders so they walk inward
            spawn_side = random.choice(['top', 'bottom', 'left', 'right'])
            if spawn_side == 'top':
                ex = random.randint(0, SCREEN_WIDTH)
                ey = -30
            elif spawn_side == 'bottom':
                ex = random.randint(0, SCREEN_WIDTH)
                ey = SCREEN_HEIGHT + 30
            elif spawn_side == 'left':
                ex = -30
                ey = random.randint(0, SCREEN_HEIGHT)
            else:
                ex = SCREEN_WIDTH + 30
                ey = random.randint(0, SCREEN_HEIGHT)
                
            self.enemies.append(Enemy(ex, ey))

    def process_combat_and_collisions(self):
        if self.state != "RUNNING":
            return

        remaining_enemies = []
        
        for enemy in self.enemies:
            # 1. Enemy attacks Player (deals 1 damage per hit context frame)
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist <= (self.player.radius + enemy.radius):
                self.player.hp = max(0, self.player.hp - 1)
                if self.player.hp <= 0:
                    self.state = "GAME_OVER"

            # 2. Player attacks Enemy (180 degree check arc)
            is_slashed = False
            if self.player.is_attacking and enemy.id not in self.player.hit_enemies_this_swing:
                # Check maximum swing target depth
                if dist - enemy.radius <= self.player.attack_range:
                    angle_to_enemy = math.atan2(dy, dx)
                    angle_diff = angle_to_enemy - self.player.facing_angle
                    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

                    # 180 degrees window math alignment (<= pi / 2)
                    if abs(angle_diff) <= math.pi / 2:
                        self.player.hit_enemies_this_swing.add(enemy.id)
                        self.score += 10
                        is_slashed = True # Enemy gets deleted/defeated
            
            if not is_slashed:
                remaining_enemies.append(enemy)

        self.enemies = remaining_enemies

        # Advance wave if room cleared out completely
        if len(self.enemies) == 0 and self.state == "RUNNING":
            self.start_next_wave()

    def update(self):
        if self.state == "RUNNING":
            self.player.handle_input()
            self.player.update()
            for enemy in self.enemies:
                enemy.update(self.player.x, self.player.y)
            self.process_combat_and_collisions()
        else:
            # Restart game via SPACE key when dead
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.__init__()

    def draw_hud(self, surface):
        # Top Left info labels
        font = pygame.font.SysFont("Arial", 18, bold=True)
        wave_surf = font.render(f"WAVE: {self.wave}", True, TEXT_COLOR)
        score_surf = font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        hp_text_surf = font.render(f"HP: {self.player.hp} / 500", True, TEXT_COLOR)
        
        surface.blit(wave_surf, (25, 20))
        surface.blit(score_surf, (25, 45))
        surface.blit(hp_text_surf, (25, 70))

        # Bottom Main Healthbar Frame
        bar_w = 400
        bar_h = 22
        bx = (SCREEN_WIDTH - bar_w) // 2
        by = SCREEN_HEIGHT - 45
        
        pygame.draw.rect(surface, OUTLINE_COLOR, (bx - 2, by - 2, bar_w + 4, bar_h + 4))
        pygame.draw.rect(surface, HEALTH_BAR_BG, (bx, by, bar_w, bar_h))
        fill_w = int(bar_w * (self.player.hp / self.player.max_hp))
        if fill_w > 0:
            pygame.draw.rect(surface, HEALTH_BAR_FILL, (bx, by, fill_w, bar_h))

        # Game Over text overlay screen
        if self.state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            surface.blit(overlay, (0,0))
            
            go_font = pygame.font.SysFont("Arial", 48, bold=True)
            sub_font = pygame.font.SysFont("Arial", 22)
            
            go_surf = go_font.render("YOU WERE OVERRUN", True, (231, 76, 60))