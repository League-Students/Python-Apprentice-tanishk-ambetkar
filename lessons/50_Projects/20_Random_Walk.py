import pygame
import math
import sys
import random

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
BG_COLOR = (34, 40, 49)
PLAYER_BODY = (52, 152, 219)
PLAYER_DARK = (41, 128, 185)
ENEMY_BODY = (231, 76, 60)
ENEMY_DARK = (192, 57, 43)
ENEMY_HIT_COLOR = (255, 255, 255)

OUTLINE_COLOR = (23, 23, 23)
EYE_COLOR = (255, 255, 255)
PUPIL_COLOR = (0, 0, 0)

SWORD_BLADE = (236, 240, 241)
SWORD_HILT = (241, 196, 15)
SWORD_GUARD = (230, 126, 34)
ARC_COLOR = (241, 196, 15)

HEALTH_BAR_BG = (50, 50, 50)
HEALTH_BAR_FILL = (46, 204, 113)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 24
        self.speed = 4.5
        self.facing_angle = 0.0
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 12
        self.attack_range = 80
        self.hit_registered = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1

        # Normalize diagonal movement speed
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Keep player on screen
        self.x = max(self.radius + 10, min(SCREEN_WIDTH - self.radius - 10, self.x))
        self.y = max(self.radius + 10, min(SCREEN_HEIGHT - self.radius - 10, self.y))

        # Aim at mouse cursor
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.facing_angle = math.atan2(mouse_y - self.y, mouse_x - self.x)

        # Attack on left click
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.hit_registered = False

    def update(self):
        if self.is_attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.is_attacking = False

    def draw(self, surface):
        # 1. Draw attack swing visual effect
        if self.is_attacking:
            start_angle = -self.facing_angle - math.pi / 2
            end_angle = -self.facing_angle + math.pi / 2
            arc_rect = pygame.Rect(self.x - self.attack_range, self.y - self.attack_range, 
                                   self.attack_range * 2, self.attack_range * 2)
            pygame.draw.arc(surface, ARC_COLOR, arc_rect, start_angle, end_angle, 4)

        # 2. Draw Weapon (Sword Sprite Details)
        # Shift sword rotation dynamically forward if attacking to simulate a swing arc
        swing_offset = 0
        if self.is_attacking:
            # Swing from left (-45 deg) to right (+45 deg) across duration
            progress = (self.attack_duration - self.attack_timer) / self.attack_duration
            swing_offset = (-math.pi / 4) + (progress * (math.pi / 2))

        render_angle = self.facing_angle + swing_offset
        
        # Calculate sword geometry points
        hilt_end_x = self.x + math.cos(render_angle) * self.radius
        hilt_end_y = self.y + math.sin(render_angle) * self.radius
        tip_x = self.x + math.cos(render_angle) * (self.radius + 40)
        tip_y = self.y + math.sin(render_angle) * (self.radius + 40)
        
        # Guard line perpendicular to blade
        guard_angle = render_angle + math.pi / 2
        g_x1 = hilt_end_x + math.cos(guard_angle) * 12
        g_y1 = hilt_end_y + math.sin(guard_angle) * 12
        g_x2 = hilt_end_x - math.cos(guard_angle) * 12
        g_y2 = hilt_end_y - math.sin(guard_angle) * 12

        # Draw weapon parts
        pygame.draw.line(surface, SWORD_BLADE, (int(hilt_end_x), int(hilt_end_y)), (int(tip_x), int(tip_y)), 5)
        pygame.draw.line(surface, SWORD_GUARD, (int(g_x1), int(g_y1)), (int(g_x2), int(g_y2)), 4)
        pygame.draw.circle(surface, SWORD_HILT, (int(self.x + math.cos(render_angle) * (self.radius - 5)), int(self.y + math.sin(render_angle) * (self.radius - 5))), 4)

        # 3. Draw Character Body (Base, shading, and black outer outline)
        pygame.draw.circle(surface, OUTLINE_COLOR, (int(self.x), int(self.y)), self.radius + 2)
        pygame.draw.circle(surface, PLAYER_BODY, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, PLAYER_DARK, (int(self.x), int(self.y)), self.radius - 4)

        # 4. Draw Character Face/Eyes looking at target angle
        for eye_side in [-1, 1]: # Left and Right eye shifts
            eye_angle = self.facing_angle + (eye_side * 0.35)
            eye_x = self.x + math.cos(eye_angle) * (self.radius - 8)
            eye_y = self.y + math.sin(eye_angle) * (self.radius - 8)
            
            # White sclera outline and fill
            pygame.draw.circle(surface, OUTLINE_COLOR, (int(eye_x), int(eye_y)), 6)
            pygame.draw.circle(surface, EYE_COLOR, (int(eye_x), int(eye_y)), 5)
            
            # Pupil tracking target slightly forward
            pupil_x = eye_x + math.cos(self.facing_angle) * 2
            pupil_y = eye_y + math.sin(self.facing_angle) * 2
            pygame.draw.circle(surface, PUPIL_COLOR, (int(pupil_x), int(pupil_y)), 2.5)


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 26
        self.speed = 2.2 # Speed relative to player balance
        self.facing_angle = 0.0
        self.max_hp = 100
        self.hp = self.max_hp
        self.flash_timer = 0

    def move_towards_target(self, target_x, target_y):
        # Calculate angle to target player
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        self.facing_angle = math.atan2(dy, dx)

        # Move closer if outside immediate touching buffer zone
        if distance > self.radius + 15:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.flash_timer = 10

    def update(self, player_obj):
        if self.flash_timer > 0:
            self.flash_timer -= 1
            
        if self.hp <= 0:
            # Respawn at random off-screen or distant coordinate when killed
            self.x = random.choice([50, SCREEN_WIDTH - 50])
            self.y = random.choice([50, SCREEN_HEIGHT - 50])
            self.hp = self.max_hp
        else:
            self.move_towards_target(player_obj.x, player_obj.y)

    def draw(self, surface):
        # Flashing evaluation color
        body_color = ENEMY_HIT_COLOR if self.flash_timer > 0 else ENEMY_BODY
        dark_color = ENEMY_HIT_COLOR if self.flash_timer > 0 else ENEMY_DARK

        # 1. Draw Enemy Base Body Outline & Shading
        pygame.draw.circle(surface, OUTLINE_COLOR, (int(self.x), int(self.y)), self.radius + 2)
        pygame.draw.circle(surface, body_color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, dark_color, (int(self.x), int(self.y)), self.radius - 5)

        # 2. Draw Angry/Tracking Eyes facing Player
        for eye_side in [-1, 1]:
            eye_angle = self.facing_angle + (eye_side * 0.38)
            eye_x = self.x + math.cos(eye_angle) * (self.radius - 9)
            eye_y = self.y + math.sin(eye_angle) * (self.radius - 9)
            
            pygame.draw.circle(surface, OUTLINE_COLOR, (int(eye_x), int(eye_y)), 6)
            pygame.draw.circle(surface, EYE_COLOR, (int(eye_x), int(eye_y)), 5)
            
            pupil_x = eye_x + math.cos(self.facing_angle) * 2.5
            pupil_y = eye_y + math.sin(self.facing_angle) * 2.5
            pygame.draw.circle(surface, PUPIL_COLOR, (int(pupil_x), int(pupil_y)), 3)

        # 3. Render Floating Top Status Healthbar
        bar_width = 54
        bar_height = 7
        bar_x = self.x - bar_width / 2
        bar_y = self.y - self.radius - 16
        
        pygame.draw.rect(surface, OUTLINE_COLOR, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        pygame.draw.rect(surface, HEALTH_BAR_BG, (bar_x, bar_y, bar_width, bar_height))
        fill_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, HEALTH_BAR_FILL, (bar_x, bar_y, fill_width, bar_height))


def check_combat(player, enemy):
    if not player.is_attacking or player.hit_registered:
        return

    dx = enemy.x - player.x
    dy = enemy.y - player.y
    distance = math.sqrt(dx**2 + dy**2)

    # Combat hitbox range logic
    if distance - enemy.radius > player.attack_range:
        return

    # Check the 180 degree arc alignment
    angle_to_enemy = math.atan2(dy, dx)
    angle_diff = angle_to_enemy - player.facing_angle
    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

    if abs(angle_diff) <= math.pi / 2:
        enemy.take_damage(20)
        player.hit_registered = True


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Detailed Combat & Enemy AI Script")
    clock = pygame.time.Clock()

    player = Player(200, 300)
    enemy = Enemy(600, 300)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update Positions and Action Loops
        player.handle_input()
        player.update()
        enemy.update(player)
        check_combat(player, enemy)

        # Screen Draw Setup
        screen.fill(BG_COLOR)
        
        # Render Sprites
        enemy.draw(screen)
        player.draw(screen)

        # Top Overlay Instructions HUD
        font = pygame.font.SysFont("Arial", 16, bold=True)