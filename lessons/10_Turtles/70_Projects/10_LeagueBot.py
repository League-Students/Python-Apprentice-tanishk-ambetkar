import pygame
import random
import sys
import math

# 1. Initialize Pygame Engine
pygame.init()

# Display Config
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BG = (30, 20, 30)      # Dark purple dungeon style
COLOR_PLAYER = (50, 150, 255) # Knight Blue
COLOR_ENEMY = (255, 60, 60)   # Fiery Enemy Red
COLOR_SWORD = (240, 240, 250) # Steel White
COLOR_UI = (255, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Combat: Defeat the Horde!")
clock = pygame.time.Clock()
font_main = pygame.font.SysFont("Arial", 28, bold=True)
font_sub = pygame.font.SysFont("Arial", 20)

# 2. Game Classes
class Player:
    def __init__(self):
        self.width = 40
        self.height = 50
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed = 5
        
        # --- BUFFED HEALTH VALUES (5x original health) ---
        self.hp = 500          
        self.max_hp = 500      
        
        self.direction = "right"
        
        # Combat parameters
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 12  # Frames the sword swings
        self.attack_cooldown = 0
        self.sword_reach = 65

    def draw(self):
        # Draw Player Core Body Rectangle
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, COLOR_PLAYER, player_rect, border_radius=6)
        
        # Draw Visor/Eyes to show direction
        eye_y = self.y + 12
        if self.direction == "right":
            pygame.draw.rect(screen, (255, 255, 0), (self.x + self.width - 12, eye_y, 8, 6))
        else:
            pygame.draw.rect(screen, (255, 255, 0), (self.x + 4, eye_y, 8, 6))

        # Draw Sword Swing Visual Arc
        if self.is_attacking:
            sword_y = self.y + self.height // 2
            # Swing right or left depending on direction face
            if self.direction == "right":
                sword_rect = pygame.Rect(self.x + self.width, sword_y - 15, self.sword_reach, 30)
            else:
                sword_rect = pygame.Rect(self.x - self.sword_reach, sword_y - 15, self.sword_reach, 30)
            pygame.draw.ellipse(screen, COLOR_SWORD, sword_rect)

    def update(self, keys):
        # Movement controls
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
            self.direction = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
            self.direction = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed

        # Screen boundaries check
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x + dx))
        self.y = max(80, min(SCREEN_HEIGHT - self.height, self.y + dy)) # Leave top room for UI

        # Timers tracking
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if self.is_attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.is_attacking = False

    def attack(self):
        if self.attack_cooldown == 0 and not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.attack_cooldown = 20  # Delay before next allowed attack

class Enemy:
    def __init__(self, player_x, player_y):
        self.width = 35
        self.height = 45
        
        # Spawn enemies randomly along perimeter edges to avoid dropping directly on player
        if random.choice([True, False]):
            self.x = random.choice([-50, SCREEN_WIDTH + 50])
            self.y = random.randint(100, SCREEN_HEIGHT - 50)
        else:
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.choice([50, SCREEN_HEIGHT + 50])
            
        self.speed = random.uniform(1.8, 3.2)
        self.hp = 30
        self.max_hp = 30
        self.damage = 1

    def draw(self):
        # Draw Monster Body
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, COLOR_ENEMY, enemy_rect, border_radius=4)
        
        # Draw Mini Health Bar over enemy head
        bar_w = self.width
        bar_h = 4
        filled_w = int(bar_w * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (100, 0, 0), (self.x, self.y - 10, bar_w, bar_h))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, filled_w, bar_h))

    def move_towards_player(self, player):
        # Calculate directional tracking vector to player coordinates
        target_x = player.x + player.width // 2 - self.width // 2
        target_y = player.y + player.height // 2 - self.height // 2
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

# 3. Game Engine Loop Execution
def main():
    player = Player()
    enemies = []
    score = 0
    wave = 1
    game_over = False

    def spawn_wave(wave_num):
        # Total enemies scaling dynamically based on current level round
        count = 3 + (wave_num * 2)
        for _ in range(count):
            enemies.append(Enemy(player.x, player.y))

    spawn_wave(wave)

    while True:
        clock.tick(FPS)
        screen.fill(COLOR_BG)

        # Event tracking loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                # Trigger sword swing attack
                if event.key == pygame.K_SPACE and not game_over:
                    player.attack()
                # Restart hotkey command logic
                if event.key == pygame.K_r and game_over:
                    main()

        if not game_over:
            # Dynamic movement engine inputs
            keys = pygame.key.get_pressed()
            player.update(keys)

            # Check if all enemies defeated -> Next Wave
            if len(enemies) == 0:
                wave += 1
                spawn_wave(wave)

            # Process Enemies Loop
            for enemy in enemies[:]:
                enemy.move_towards_player(player)

                # 1. Collision check: Enemy hits player shield/armor
                p_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                e_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if p_rect.colliderect(e_rect):
                    player.hp -= enemy.damage
                    if player.hp <= 0:
                        game_over = True

                # 2. Collision check: Player sword swing strikes enemy body
                if player.is_attacking and player.attack_timer == player.attack_duration:
                    # Establish physical rectangle of weapon sweep reach zone
                    sword_y = player.y + player.height // 2
                    if player.direction == "right":
                        hitbox = pygame.Rect(player.x + player.width, sword_y - 20, player.sword_reach, 40)
                    else:
                        hitbox = pygame.Rect(player.x - player.sword_reach, sword_y - 20, player.sword_reach, 40)

                    if hitbox.colliderect(e_rect):
                        enemy.hp -= 15  # Deal damage
                        if enemy.hp <= 0:
                            enemies.remove(enemy)
                            score += 50

        # --- DRAW VISUAL LAYERS ---
        # Draw actors
        for enemy in enemies:
            enemy.draw()
        player.draw()

        # Draw HUD interface header bar background
        pygame.draw.rect(screen, (15, 10, 20), (0, 0, SCREEN_WIDTH, 70))
        
        # Draw Player HP bar layout
        hp_text = font_sub.render(f"HP: {max(0, player.hp)} / {player.max_hp}", True, COLOR_UI)
        screen.blit(hp_text, (20, 22))
        pygame.draw.rect(screen, (80, 20, 20), (180, 25, 200, 16)) # Red backing fill
        player_hp_w = max(0, int(200 * (player.hp / player.max_hp)))
        pygame.draw.rect(screen, (50, 220, 90), (180, 25, player_hp_w, 16)) # Live green foreground

        # Draw HUD text elements
        score_surface = font_main.render(f"SCORE: {score}", True, COLOR_UI)
        wave_surface = font_main.render(f"WAVE: {wave}", True, (230, 180, 50))
        screen.blit(score_surface, (420, 18))
        screen.blit(wave_surface, (740, 18))

        # Game Over Interface Overlay
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)) # Dark transparent dimming filter
            screen.blit(overlay, (0, 0))
            
            go_text = font_main.render("YOU WERE OVERRUN!", True, (255, 50, 50))
            restart_text = font_sub.render("Press 'R' to Restart and Fight Again", True, COLOR_UI)
            
            screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()

if __name__ == "__main__":
    main()