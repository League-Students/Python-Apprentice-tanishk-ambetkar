import pygame
import random
import sys

# 1. Initialize Pygame engine
pygame.init()

# Game Window Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Design Elements (RGB Colors)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)

# Set up display surface
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Arcade Shooter")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)

# 2. Define Game Classes
class Player:
    def __init__(self):
        self.width = 50
        self.height = 40
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 60
        self.speed = 7

    def draw(self):
        # Draw player as a sleek green spaceship triangle/polygon
        points = [
            (self.x + self.width // 2, self.y), 
            (self.x, self.y + self.height), 
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, COLOR_GREEN, points)

    def move(self, keys):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 0:
            self.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

class Laser:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 15
        self.speed = 10

    def draw(self):
        pygame.draw.rect(screen, COLOR_YELLOW, (self.x, self.y, self.width, self.height))

    def update(self):
        self.y -= self.speed

class Enemy:
    def __init__(self):
        self.width = 40
        self.height = 30
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = random.randint(-150, -40)
        self.speed = random.randint(3, 6)

    def draw(self):
        pygame.draw.rect(screen, COLOR_RED, (self.x, self.y, self.width, self.height), border_radius=5)

    def update(self):
        self.y += self.speed

# 3. Main Game Loop Setup
def main():
    player = Player()
    lasers = []
    enemies = []
    score = 0
    game_over = False

    # Spawn initial wave of enemies
    for _ in range(6):
        enemies.append(Enemy())

    while True:
        # Tick the clock to lock frame rate
        clock.tick(FPS)
        screen.fill(COLOR_BLACK)

        # Handle Events (Input Monitoring)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Fire lasers when Spacebar is pressed
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_SPACE:
                    laser_x = player.x + player.width // 2 - 2
                    lasers.append(Laser(laser_x, player.y))
                
                # Restart game tracking if player presses R after dying
                if event.key == pygame.K_r and game_over:
                    main()

        if not game_over:
            # Read continuous keyboard movement inputs
            keys = pygame.key.get_pressed()
            player.move(keys)

            # Update Lasers position and cleanup offscreen objects
            for laser in lasers[:]:
                laser.update()
                if laser.y < 0:
                    lasers.remove(laser)

            # Update Enemy positions
            for enemy in enemies[:]:
                enemy.update()
                
                # Respawn enemy at top if it flies past bottom boundary
                if enemy.y > SCREEN_HEIGHT:
                    enemies.remove(enemy)
                    enemies.append(Enemy())

                # Game Over condition: Enemy collides with the player spaceship
                player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if player_rect.colliderect(enemy_rect):
                    game_over = True

            # Collision Detection: Check if Lasers hit Enemies
            for laser in lasers[:]:
                laser_rect = pygame.Rect(laser.x, laser.y, laser.width, laser.height)
                for enemy in enemies[:]:
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                    
                    if laser_rect.colliderect(enemy_rect):
                        # Safely remove components from active tracking lists
                        if laser in lasers:
                            lasers.remove(laser)
                        enemies.remove(enemy)
                        score += 10
                        enemies.append(Enemy()) # Spawn replacement enemy

        # 4. Render Game Objects on Screen
        player.draw()
        for laser in lasers:
            laser.draw()
        for enemy in enemies:
            enemy.draw()

        # Display the live scoreboard layout
        score_text = font.render(f"Score: {score}", True, COLOR_WHITE)
        screen.blit(score_text, (10, 10))

        # Render Game Over UI Overlay
        if game_over:
            over_text = font.render("GAME OVER - Press 'R' to Restart", True, COLOR_RED)
            text_rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(over_text, text_rect)

        # Flip display buffer to show new frames
        pygame.display.flip()

if __name__ == "__main__":
    main()