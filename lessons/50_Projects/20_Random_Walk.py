import pygame
import math
import sys

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
BG_COLOR = (40, 44, 52)
PLAYER_COLOR = (52, 152, 219)
ENEMY_COLOR = (231, 76, 60)
ENEMY_HIT_COLOR = (255, 255, 255)
SWORD_COLOR = (241, 196, 15)
ARC_COLOR = (241, 196, 15, 50) # Translucent yellow
TEXT_COLOR = (255, 255, 255)
HEALTH_BAR_BG = (100, 100, 100)
HEALTH_BAR_FILL = (46, 204, 113)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.speed = 4
        self.facing_angle = 0.0  # Angle in radians pointing to mouse
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 15  # Frames the attack animation lasts
        self.attack_range = 70
        self.hit_registered = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: self.x -= self.speed
        if keys[pygame.K_d]: self.x += self.speed
        if keys[pygame.K_w]: self.y -= self.speed
        if keys[pygame.K_s]: self.y += self.speed

        # Keep player on screen
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

        # Update facing angle toward mouse cursor
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.facing_angle = math.atan2(mouse_y - self.y, mouse_x - self.x)

        # Trigger attack on Left Click
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
        # Draw 180-degree attack zone visualization when attacking
        if self.is_attacking:
            # Pygame arc uses standard math angles, but inverted Y-axis.
            # 180 degrees = math.pi radians total (Spread: -pi/2 to +pi/2 relative to facing angle)
            start_angle = -self.facing_angle - math.pi / 2
            end_angle = -self.facing_angle + math.pi / 2
            
            arc_rect = pygame.Rect(self.x - self.attack_range, self.y - self.attack_range, 
                                   self.attack_range * 2, self.attack_range * 2)
            pygame.draw.arc(surface, SWORD_COLOR, arc_rect, start_angle, end_angle, 3)

        # Draw Player body
        pygame.draw.circle(surface, PLAYER_COLOR, (int(self.x), int(self.y)), self.radius)
        
        # Draw weapon directional line
        line_end_x = self.x + math.cos(self.facing_angle) * (self.radius + 15)
        line_end_y = self.y + math.sin(self.facing_angle) * (self.radius + 15)
        pygame.draw.line(surface, SWORD_COLOR, (self.x, self.y), (line_end_x, line_end_y), 4)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.max_hp = 100
        self.hp = self.max_hp
        self.flash_timer = 0

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.flash_timer = 10  # Flash white for 10 frames

    def update(self):
        if self.flash_timer > 0:
            self.flash_timer -= 1
        if self.hp <= 0:
            # Respawn enemy at a random location if defeated
            import random
            self.x = random.randint(100, SCREEN_WIDTH - 100)
            self.y = random.randint(100, SCREEN_HEIGHT - 100)
            self.hp = self.max_hp

    def draw(self, surface):
        # Determine color based on hit flashing
        color = ENEMY_HIT_COLOR if self.flash_timer > 0 else ENEMY_COLOR
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)

        # Draw health bar above enemy
        bar_width = 50
        bar_height = 6
        bar_x = self.x - bar_width / 2
        bar_y = self.y - self.radius - 15
        
        pygame.draw.rect(surface, HEALTH_BAR_BG, (bar_x, bar_y, bar_width, bar_height))
        fill_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, HEALTH_BAR_FILL, (bar_x, bar_y, fill_width, bar_height))


def check_combat(player, enemy):
    """Checks if the enemy is inside the player's 180-degree attack arc."""
    if not player.is_attacking or player.hit_registered:
        return

    # 1. Check distance
    dx = enemy.x - player.x
    dy = enemy.y - player.y
    distance = math.sqrt(dx**2 + dy**2)

    # Check distance to enemy edge, not just center
    if distance - enemy.radius > player.attack_range:
        return

    # 2. Check angle
    # Angle from player pointing directly to enemy
    angle_to_enemy = math.atan2(dy, dx)
    
    # Calculate difference between player facing direction and enemy position
    angle_diff = angle_to_enemy - player.facing_angle
    
    # Normalize angle difference to be between -pi and pi
    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

    # If the absolute difference is less than 90 degrees (pi/2 radians), 
    # the enemy falls inside the 180-degree forward arc.
    if abs(angle_diff) <= math.pi / 2:
        enemy.take_damage(25)
        player.hit_registered = True  # Prevent multiple hits in a single swing


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("180 Degree Combat Script")
    clock = pygame.time.Clock()

    player = Player(200, 300)
    enemy = Enemy(500, 300)

    # Main Loop
    while True:
        # Event tracking
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update Logic
        player.handle_input()
        player.update()
        enemy.update()
        check_combat(player, enemy)

        # Rendering
        screen.fill(BG_COLOR)
        
        # Draw game objects
        enemy.draw(screen)
        player.draw(screen)

        # Control text instructions
        font = pygame.font.SysFont("Arial", 18)
        inst_text = font.render("Controls: WASD to Move | Mouse to Aim | Left Click to Attack (180° Front Arc)", True, TEXT_COLOR)
        screen.blit(inst_text, (15, 15))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()