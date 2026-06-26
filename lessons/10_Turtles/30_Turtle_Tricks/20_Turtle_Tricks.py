import pygame
import math
import sys
import random

# Initialize core frameworks safely
pygame.init()

# Setup display window constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
FPS = 60

# Safe Platform Colors (RGB)
BG_COLOR = (24, 28, 36)
PLAYER_MAIN = (52, 152, 219)
PLAYER_DARK = (41, 128, 185)
ENEMY_BASE = (231, 76, 60)
OUTLINE_DARK = (16, 16, 18)
COIN_GOLD = (241, 196, 15)

# Pet Tier Multipliers
COLOR_COMMON = (46, 204, 113)
COLOR_RARE = (155, 89, 182)
COLOR_LEGENDARY = (230, 126, 34)

# Weapon Tier Aesthetics
TIER_COLORS = [
    (139, 69, 19),    # Tier 1: Wooden Blade (Brown)
    (192, 192, 192),  # Tier 2: Steel Saber (Silver)
    (255, 215, 0),    # Tier 3: Gold Cleaver (Gold)
    (142, 68, 173)    # Tier 4: Void Greatsword (Purple Glow)
]
TIER_NAMES = ["Wooden Blade", "Steel Saber", "Gold Cleaver", "Void Greatsword"]

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 22
        self.speed = 4.0
        self.facing_angle = 0.0
        self.max_hp = 500
        self.hp = self.max_hp
        
        # Progression & Stats
        self.base_damage = 25
        self.attack_range = 80
        self.coins = 0
        self.weapon_tier = 0
        self.active_pet = None  # Holds active companion tier info
        
        # Combat setup
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 9  
        self.hit_targets_this_swing = set()

    def get_total_damage(self):
        # Calculate bonus based on sword tier level and hatched pets
        multiplier = 1.0
        if self.active_pet == "Common": multiplier = 1.5
        elif self.active_pet == "Rare": multiplier = 2.5
        elif self.active_pet == "Legendary": multiplier = 5.0
        
        tier_bonus = 1.0 + (self.weapon_tier * 0.8)
        return int(self.base_damage * tier_bonus * multiplier)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx * self.speed
        self.y += dy * self.speed

        self.x = max(self.radius + 15, min(SCREEN_WIDTH - self.radius - 15, self.x))
        self.y = max(self.radius + 15, min(SCREEN_HEIGHT - self.radius - 15, self.y))

        # Aim heading calculation
        m_x, m_y = pygame.mouse.get_pos()
        self.facing_angle = math.atan2(m_y - self.y, m_x - self.x)

        # Attack on left click
        m_buttons = pygame.mouse.get_pressed()
        if m_buttons[0] and not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.hit_targets_this_swing.clear()

    def update(self):
        if self.is_attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.is_attacking = False
                
        # Automatic Sword Mastery Evolutions based on collected loot thresholds
        if self.coins >= 1200 and self.weapon_tier == 2:
            self.weapon_tier = 3
        elif self.coins >= 400 and self.weapon_tier == 1:
            self.weapon_tier = 2
        elif self.coins >= 100 and self.weapon_tier == 0:
            self.weapon_tier = 1

    def draw(self, surface):
        # 1. 180-Degree Strike Field Arc 
        if self.is_attacking:
            start = -self.facing_angle - math.pi / 2
            end = -self.facing_angle + math.pi / 2
            arc_rect = pygame.Rect(self.x - self.attack_range, self.y - self.attack_range, 
                                   self.attack_range * 2, self.attack_range * 2)
            pygame.draw.arc(surface, TIER_COLORS[self.weapon_tier], arc_rect, start, end, 4)

        # 2. Render Hatched Floating Pet Companion
        if self.active_pet:
            pet_color = COLOR_COMMON
            if self.active_pet == "Rare": pet_color = COLOR_RARE
            elif self.active_pet == "Legendary": pet_color = COLOR_LEGENDARY
            
            # Orbit location behind player circle
            pet_x = self.x + math.cos(self.facing_angle + math.pi) * 35
            pet_y = self.y + math.sin(self.facing_angle + math.pi) * 35
            pygame.draw.circle(surface, OUTLINE_DARK, (int(pet_x), int(pet_y)), 9)
            pygame.draw.circle(surface, pet_color, (int(pet_x), int(pet_y)), 7)

        # 3. Dynamic Sword Tracking Position
        offset = 0
        if self.is_attacking:
            prog = (self.attack_duration - self.attack_timer) / self.attack_duration
            offset = (-math.pi / 4) + (prog * (math.pi / 2))

        w_angle = self.facing_angle + offset
        hx = self.x + math.cos(w_angle) * self.radius
        hy = self.y + math.sin(w_angle) * self.radius
        tx = self.x + math.cos(w_angle) * (self.radius + 40)
        ty = self.y + math.sin(w_angle) * (self.radius + 40)
        pygame.draw.line(surface, TIER_COLORS[self.weapon_tier], (int(hx), int(hy)), (int(tx), int(ty)), 6)

        # 4. Player Sprite Shell
        pygame.draw.circle(surface, OUTLINE_DARK, (int(self.x), int(self.y)), self.radius + 2)
        pygame.draw.circle(surface, PLAYER_MAIN, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, PLAYER_DARK, (int(self.x), int(self.y)), self.radius - 5)


class Enemy:
    def __init__(self, x, y, wave_number):
        self.x = x
        self.y = y
        self.radius = 15
        self.speed = random.uniform(1.6, 2.3)
        # Scaled health pools for high wave progression
        self.max_hp = 20 + (wave_number * 15)
        self.hp = self.max_hp
        self.id = random.random()

    def update(self, px, py):
        dx = px - self.x
        dy = py - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, OUTLINE_DARK, (int(self.x), int(self.y)), self.radius + 2)
        pygame.draw.circle(surface, ENEMY_BASE, (int(self.x), int(self.y)), self.radius)


class GameController:
    def __init__(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.wave = 0
        self.state = "RUNNING"
        
        # Hatchery Coordinates (Top right interactable block)
        self.egg_x = 750
        self.egg_y = 120
        self.egg_radius = 35
        self.egg_cost = 50
        
        # Universal Local Fonts
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 56)
        
        self.start_next_wave()

    def start_next_wave(self):
        self.wave += 1
        for _ in range(self.wave * 4):
            side = random.choice(['t', 'b', 'l', 'r'])
            if side == 't': ex, ey = random.randint(0, SCREEN_WIDTH), -25
            elif side == 'b': ex, ey = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 25
            elif side == 'l': ex, ey = -25, random.randint(0, SCREEN_HEIGHT)
            else: ex, ey = SCREEN_WIDTH + 25, random.randint(0, SCREEN_HEIGHT)
            self.enemies.append(Enemy(ex, ey, self.wave))

    def process_logic(self):
        if self.state != "RUNNING": return

        # Check for upgrade inputs (U Key)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_u] and self.player.coins >= 30:
            self.player.coins -= 30
            self.player.base_damage += 10
            self.player.attack_range += 4

        # Check for Egg Open inputs (E Key near hatchery zone)
        dx = self.player.x - self.egg_x
        dy = self.player.y - self.egg_y
        if math.sqrt(dx**2 + dy**2) <= self.player.radius + self.egg_radius:
            if keys[pygame.K_e] and self.player.player_is_trigger-ready(): # Checked loop handler via event tracker
                pass

        alive_enemies = []
        for enemy in self.enemies:
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            dist = math.sqrt(dx**2 + dy**2)
            
            # Contact frame check: Minions deal exactly 1 damage per hit context frame
            if dist <= (self.player.radius + enemy.radius):
                self.player.hp = max(0, self.player.hp - 1)
                if self.player.hp <= 0: self.state = "GAME_OVER"

            is_killed = False
            if self.player.is_attacking and enemy.id not in self.player.hit_targets_this_swing:
                if dist - enemy.radius <= self.player.attack_range:
                    angle_to_enemy = math.atan2(dy, dx)
                    diff = angle_to_enemy - self.player.facing_angle
                    diff = (diff + math.pi) % (2 * math.pi) - math.pi

                    # 180-degree front check calculation
                    if abs(diff) <= math.pi / 2:
                        self.player.hit_targets_this_swing.add(enemy.id)
                        enemy.hp -= self.player.get_total_damage()
                        if enemy.hp <= 0:
                            self.player.coins += random.randint(8, 15) # Extracted gold loot
                            is_killed = True
            
            if not is_killed: alive_enemies.append(enemy)

        self.enemies = alive_enemies
        if len(self.enemies) == 0 and self.state == "RUNNING":
            self.start_next_wave()

    def trigger_egg_hatch(self):
        """Hatch logic based on classic Sword Masters RNG drop weight rates."""
        if self.player.coins >= self.egg_cost:
            self.player.coins -= self.egg_cost
            roll = random.random()
            if roll < 0.60: self.player.active_pet = "Common"    # 60% Chance
            elif roll < 0.90: self.player.active_pet = "Rare"   # 30% Chance