# Professional Spaceship Combat Game with AI Bot

import pygame
import os
import math
import random
import time

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Clash")

# Professional Color Palette
DARK_NAVY = (15, 20, 35)
STEEL_BLUE = (70, 130, 180)
CRIMSON = (220, 20, 60)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (60, 60, 60)
SILVER = (192, 192, 192)
AMBER = (255, 191, 0)
CHARCOAL = (36, 36, 36)

# Minimal particle system for subtle effects
class Particle:
    def __init__(self, x, y, color, size=1, lifetime=30, velocity=None):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.velocity = velocity or [random.uniform(-1, 1), random.uniform(-1, 1)]

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color[:3], (int(self.x), int(self.y)), self.size)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_impact(self, x, y, color, count=6):
        for _ in range(count):
            velocity = [random.uniform(-2, 2), random.uniform(-2, 2)]
            size = random.randint(1, 2)
            lifetime = random.randint(15, 25)
            self.particles.append(Particle(x, y, color, size, lifetime, velocity))

    def add_exhaust(self, x, y, color, direction=1):
        if random.randint(1, 3) == 1:  # Less frequent exhaust
            velocity = [direction * random.uniform(-0.5, -1.5), random.uniform(-0.3, 0.3)]
            size = 1
            lifetime = random.randint(10, 20)
            self.particles.append(Particle(x, y, color, size, lifetime, velocity))

    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# Professional spaceship class
class Spaceship:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit_flash = 0

    def update(self):
        if self.hit_flash > 0:
            self.hit_flash -= 8

    def hit(self):
        self.hit_flash = 120

    def draw(self, surface):
        # Draw hit flash as subtle outline
        if self.hit_flash > 0:
            flash_rect = pygame.Rect(self.rect.x - 2, self.rect.y - 2, 
                                   self.rect.width + 4, self.rect.height + 4)
            pygame.draw.rect(surface, WHITE, flash_rect, 2)

        # Draw main spaceship body
        pygame.draw.rect(surface, self.color, self.rect)

        # Add subtle highlight
        highlight_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, 
                                   self.rect.width - 4, self.rect.height // 3)
        highlight_color = tuple(min(255, c + 40) for c in self.color)
        pygame.draw.rect(surface, highlight_color, highlight_rect)

        # Add border for definition
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, 1)

# AI Bot class for yellow player with smooth movement
class AIBot:
    def __init__(self, difficulty=1):
        self.difficulty = difficulty  # 1=Easy, 2=Medium, 3=Hard
        self.reaction_delay = 0
        self.last_shot_time = 0  # Start with 0 so bot can shoot immediately
        self.evasion_timer = 0
        self.target_y = 0
        
        # Smooth movement variables
        self.current_direction_x = 0  # -1, 0, 1
        self.current_direction_y = 0  # -1, 0, 1
        self.movement_consistency_timer = 0
        self.last_decision_time = 0
        self.decision_cooldown = 10  # Frames to wait before changing direction
        
        # Movement smoothing
        self.velocity_x = 0
        self.velocity_y = 0
        self.max_velocity = 3
        self.acceleration = 0.3
        self.deceleration = 0.8
        
    def calculate_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def predict_target_position(self, target_rect, target_velocity=None):
        # Simple prediction - assumes target continues current direction
        if target_velocity:
            prediction_time = 0.5  # Predict 0.5 seconds ahead
            predicted_x = target_rect.centerx + target_velocity[0] * prediction_time
            predicted_y = target_rect.centery + target_velocity[1] * prediction_time
            return (predicted_x, predicted_y)
        return target_rect.center
    
    def should_shoot(self, yellow_rect, red_rect, yellow_bullets):
        current_time = time.time()
        
        # Rate limiting based on difficulty (reduced cooldowns for more shooting)
        shoot_cooldown = {1: 0.4, 2: 0.3, 3: 0.2}
        if current_time - self.last_shot_time < shoot_cooldown.get(self.difficulty, 0.3):
            return False
            
        # Don't shoot if at max bullets
        if len(yellow_bullets) >= MAX_BULLETS:
            return False
            
        # More aggressive shooting - larger alignment threshold
        vertical_alignment = abs(yellow_rect.centery - red_rect.centery)
        alignment_threshold = {1: 120, 2: 100, 3: 80}
        
        if vertical_alignment < alignment_threshold.get(self.difficulty, 100):
            # Shoot immediately without distance restrictions
            self.last_shot_time = current_time
            return True
        
        # Also shoot occasionally even when not perfectly aligned (spray and pray)
        if random.randint(1, 100) <= 15:  # 15% chance to shoot anyway
            self.last_shot_time = current_time
            return True
        
        return False
    
    def get_smooth_movement_decision(self, yellow_rect, red_rect, red_bullets):
        # Update timers
        self.movement_consistency_timer += 1
        
        # Immediate evasion for incoming bullets (override other behaviors)
        urgent_evasion = False
        for bullet in red_bullets:
            if bullet.x < yellow_rect.centerx + 120:  # Bullet is approaching
                bullet_distance = abs(bullet.centery - yellow_rect.centery)
                if bullet_distance < 60:  # Bullet is aligned with us
                    # Quick evasion decision
                    if yellow_rect.centery > HEIGHT // 2:
                        self.current_direction_y = -1  # Move up
                    else:
                        self.current_direction_y = 1   # Move down
                    self.current_direction_x = -1  # Move away from bullet
                    self.evasion_timer = 40
                    self.movement_consistency_timer = 0
                    urgent_evasion = True
                    break
        
        # If evading, maintain evasion direction for consistency
        if self.evasion_timer > 0:
            self.evasion_timer -= 1
            if not urgent_evasion:
                # Gradually reduce evasion intensity
                if self.evasion_timer < 15:
                    self.current_direction_x = 0
        else:
            # Normal strategic movement (only change direction periodically)
            if self.movement_consistency_timer >= self.decision_cooldown:
                yellow_center = yellow_rect.center
                red_center = red_rect.center
                
                # Vertical positioning
                vertical_diff = red_center[1] - yellow_center[1]
                dead_zone = 25  # Don't micro-adjust for small differences
                
                if abs(vertical_diff) > dead_zone:
                    if vertical_diff > 0:
                        self.current_direction_y = 1  # Move down
                    else:
                        self.current_direction_y = -1  # Move up
                else:
                    self.current_direction_y = 0  # Stop vertical movement
                
                # Horizontal positioning - maintain optimal distance
                horizontal_diff = red_center[0] - yellow_center[0]
                optimal_distance = 220 + (self.difficulty * 30)
                distance_tolerance = 40
                
                if horizontal_diff > optimal_distance + distance_tolerance:
                    self.current_direction_x = 1  # Move right (towards target)
                elif horizontal_diff < optimal_distance - distance_tolerance:
                    self.current_direction_x = -1  # Move left (away from target)
                else:
                    self.current_direction_x = 0  # Maintain position
                
                # Add some randomness for lower difficulties
                if self.difficulty == 1 and random.randint(1, 10) <= 3:
                    # 30% chance to make a random movement decision
                    self.current_direction_y = random.choice([-1, 0, 1])
                
                # Reset consistency timer
                self.movement_consistency_timer = 0
        
        # Apply smooth acceleration/deceleration
        target_vel_x = self.current_direction_x * self.max_velocity
        target_vel_y = self.current_direction_y * self.max_velocity
        
        # Smooth velocity changes
        if abs(target_vel_x - self.velocity_x) > 0.1:
            if target_vel_x > self.velocity_x:
                self.velocity_x += self.acceleration
            else:
                self.velocity_x -= self.acceleration
        else:
            self.velocity_x = target_vel_x
            
        if abs(target_vel_y - self.velocity_y) > 0.1:
            if target_vel_y > self.velocity_y:
                self.velocity_y += self.acceleration
            else:
                self.velocity_y -= self.acceleration
        else:
            self.velocity_y = target_vel_y
        
        # Clamp velocities
        self.velocity_x = max(-self.max_velocity, min(self.max_velocity, self.velocity_x))
        self.velocity_y = max(-self.max_velocity, min(self.max_velocity, self.velocity_y))
        
        return self.velocity_x, self.velocity_y

# Game state
BORDER = pygame.Rect(WIDTH//2 - 3, 0, 6, HEIGHT)
FPS = 60
VEL = 5
BULLET_VEL = 9
MAX_BULLETS = 10
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

# Game events
YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

# Create subtle starfield
stars = []
for _ in range(80):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.randint(1, 2)
    brightness = random.randint(120, 200)
    stars.append([x, y, size, brightness])

def draw_starfield():
    """Draw subtle starfield background"""
    for star in stars:
        color = (star[3], star[3], star[3])
        pygame.draw.circle(WIN, color, (int(star[0]), int(star[1])), star[2])

def draw_border():
    """Draw invisible center border (collision detection only)"""
    # The border is still there for collision detection, but we don't draw it
    pass

def draw_bullets(bullets, color):
    """Draw clean bullets"""
    for bullet in bullets:
        pygame.draw.rect(WIN, color, bullet)
        pygame.draw.rect(WIN, WHITE, bullet, 1)

def draw_professional_ui(red_health, yellow_health):
    """Draw clean, professional UI"""
    # Fonts
    title_font = pygame.font.Font(None, 32)
    health_font = pygame.font.Font(None, 24)

    # Player names
    yellow_title = title_font.render("AI BOT", True, GOLD)
    red_title = title_font.render("PLAYER", True, CRIMSON)

    WIN.blit(yellow_title, (30, 25))
    WIN.blit(red_title, (WIDTH - red_title.get_width() - 30, 25))

    # Health bar dimensions
    bar_width = 180
    bar_height = 16
    border_width = 2

    # Yellow player health bar (left)
    bar_x = 30
    bar_y = 60

    # Outer border
    outer_rect = pygame.Rect(bar_x - border_width, bar_y - border_width, 
                           bar_width + 2*border_width, bar_height + 2*border_width)
    pygame.draw.rect(WIN, LIGHT_GRAY, outer_rect)

    # Background
    bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(WIN, CHARCOAL, bg_rect)

    # Health fill
    health_ratio = max(0, yellow_health / 10)
    fill_width = int(bar_width * health_ratio)
    if fill_width > 0:
        health_color = GOLD if health_ratio > 0.4 else AMBER if health_ratio > 0.2 else CRIMSON
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        pygame.draw.rect(WIN, health_color, fill_rect)

    # Health text
    health_text = health_font.render(f"HEALTH: {yellow_health}/10", True, WHITE)
    WIN.blit(health_text, (bar_x, bar_y + bar_height + 8))

    # Red player health bar (right)
    bar_x = WIDTH - bar_width - 30

    # Outer border
    outer_rect = pygame.Rect(bar_x - border_width, bar_y - border_width, 
                           bar_width + 2*border_width, bar_height + 2*border_width)
    pygame.draw.rect(WIN, LIGHT_GRAY, outer_rect)

    # Background
    bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(WIN, CHARCOAL, bg_rect)

    # Health fill
    health_ratio = max(0, red_health / 10)
    fill_width = int(bar_width * health_ratio)
    if fill_width > 0:
        health_color = GOLD if health_ratio > 0.4 else AMBER if health_ratio > 0.2 else CRIMSON
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        pygame.draw.rect(WIN, health_color, fill_rect)

    # Health text
    health_text = health_font.render(f"HEALTH: {red_health}/10", True, WHITE)
    text_rect = health_text.get_rect()
    text_rect.topright = (bar_x + bar_width, bar_y + bar_height + 8)
    WIN.blit(health_text, text_rect)

    # Game title at top center
    game_title = title_font.render("  ", True, STEEL_BLUE)
    title_rect = game_title.get_rect(center=(WIDTH//2, 30))
    WIN.blit(game_title, title_rect)

def draw_winner(text):
    """Draw winner announcement professionally with separate boxes"""
    winner_font = pygame.font.Font(None, 96)
    option_font = pygame.font.Font(None, 28)

    waiting_for_input = True
    while waiting_for_input:
        WIN.fill(DARK_NAVY)
        draw_starfield()

        # -----------------------
        # Box 1: Winner Text Box
        # -----------------------
        winner_surface = winner_font.render(text, True, WHITE)
        winner_rect = winner_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))

        winner_panel = pygame.Rect(winner_rect.x - 40, winner_rect.y - 30,
                                   winner_rect.width + 80, winner_rect.height + 60)

        winner_bg = pygame.Surface((winner_panel.width, winner_panel.height))
        winner_bg.set_alpha(220)
        winner_bg.fill(CHARCOAL)
        WIN.blit(winner_bg, winner_panel)
        pygame.draw.rect(WIN, STEEL_BLUE, winner_panel, 3)
        WIN.blit(winner_surface, winner_rect)

        # --------------------------
        # Box 2: Control Options Box
        # --------------------------
        option_box_w, option_box_h = 320, 120
        option_panel = pygame.Rect((WIDTH - option_box_w) // 2, HEIGHT // 2 + 20, option_box_w, option_box_h)

        option_bg = pygame.Surface((option_box_w, option_box_h))
        option_bg.set_alpha(200)
        option_bg.fill(DARK_GRAY)
        WIN.blit(option_bg, option_panel)
        pygame.draw.rect(WIN, LIGHT_GRAY, option_panel, 2)

        # Option Texts
        option1_text = option_font.render("PRESS R - PLAY AGAIN", True, GOLD)
        option2_text = option_font.render("PRESS M - MAIN MENU", True, STEEL_BLUE)
        option3_text = option_font.render("PRESS ESC - EXIT", True, LIGHT_GRAY)

        WIN.blit(option1_text, option1_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))
        WIN.blit(option2_text, option2_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))
        WIN.blit(option3_text, option3_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                elif event.key == pygame.K_m:
                    return "menu"
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        pygame.time.Clock().tick(60)


def yellow_handle_movement(yellow, red, red_bullets, ai_bot, particle_system):
    """AI-controlled smooth movement for yellow player"""
    # Get smooth AI movement decision
    vel_x, vel_y = ai_bot.get_smooth_movement_decision(yellow.rect, red.rect, red_bullets)
    
    moved = False
    
    # Apply horizontal movement
    new_x = yellow.rect.x + vel_x
    if new_x >= 0 and new_x + yellow.rect.width <= BORDER.x:
        yellow.rect.x = new_x
        if abs(vel_x) > 0.1:
            moved = True
    
    # Apply vertical movement
    new_y = yellow.rect.y + vel_y
    if new_y >= 0 and new_y + yellow.rect.height <= HEIGHT - 15:
        yellow.rect.y = new_y
        if abs(vel_y) > 0.1:
            moved = True

    # Subtle exhaust when moving
    if moved:
        particle_system.add_exhaust(yellow.rect.x, yellow.rect.centery, GOLD, -1)

def red_handle_movement(keys_pressed, red, ai_bot, particle_system):
    moved = False
    if keys_pressed[pygame.K_LEFT] and red.rect.x - VEL > BORDER.x + BORDER.width:
        red.rect.x -= VEL
        moved = True
    if keys_pressed[pygame.K_RIGHT] and red.rect.x + VEL + red.rect.width < WIDTH:
        red.rect.x += VEL
        moved = True
    if keys_pressed[pygame.K_UP] and red.rect.y - VEL > 0:
        red.rect.y -= VEL
        moved = True
    if keys_pressed[pygame.K_DOWN] and red.rect.y + VEL + red.rect.height < HEIGHT - 15:
        red.rect.y += VEL
        moved = True

    # Subtle exhaust when moving
    if moved:
        particle_system.add_exhaust(red.rect.right, red.rect.centery, CRIMSON, 1)

def handle_bullets(yellow_bullets, red_bullets, yellow, red, ai_bot, particle_system):
    for bullet in yellow_bullets[:]:
        bullet.x += BULLET_VEL
        if red.rect.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            particle_system.add_impact(bullet.centerx, bullet.centery, CRIMSON)
            yellow_bullets.remove(bullet)
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets[:]:
        bullet.x -= BULLET_VEL
        if yellow.rect.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            particle_system.add_impact(bullet.centerx, bullet.centery, GOLD)
            red_bullets.remove(bullet)
        elif bullet.x < 0:
            red_bullets.remove(bullet)

def main():
    # Initialize particle system and AI
    ai_bot = AIBot(difficulty=1)  # Medium difficulty
    particle_system = ParticleSystem()
    
    # Create spaceships
    red_ship = Spaceship(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT, CRIMSON)
    yellow_ship = Spaceship(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT, GOLD)

    red_bullets = []
    yellow_bullets = []

    red_health = 10
    yellow_health = 10

    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                # Only human player (red) can shoot manually
                if event.key == pygame.K_SPACE and len(red_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(
                        red_ship.rect.x, red_ship.rect.y + red_ship.rect.height//2 - 2, 10, 4)
                    red_bullets.append(bullet)

            if event.type == RED_HIT:
                red_health -= 1
                red_ship.hit()

            if event.type == YELLOW_HIT:
                yellow_health -= 1
                yellow_ship.hit()

        # AI shooting logic
        if ai_bot.should_shoot(yellow_ship.rect, red_ship.rect, yellow_bullets):
            bullet = pygame.Rect(
                yellow_ship.rect.x + yellow_ship.rect.width, 
                yellow_ship.rect.y + yellow_ship.rect.height//2 - 2, 10, 4)
            yellow_bullets.append(bullet)

        # Check for winner
        winner_text = ""
        if red_health <= 0:
            winner_text = "BOT WINS"
        if yellow_health <= 0:
            winner_text = "PLAYER WINS"

        if winner_text != "":
            result = draw_winner(winner_text)
            if result == "restart":
                # Reset the game
                red_ship = Spaceship(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT, CRIMSON)
                yellow_ship = Spaceship(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT, GOLD)
                red_bullets = []
                yellow_bullets = []
                red_health = 10
                yellow_health = 10
                # Reset AI bot
                ai_bot = AIBot(difficulty=2)
                continue
            elif result == "menu":
                return "menu"
            else:
                break

        # Update game objects
        keys_pressed = pygame.key.get_pressed()
        yellow_handle_movement(yellow_ship, red_ship, red_bullets, ai_bot, particle_system)
        red_handle_movement(keys_pressed, red_ship, ai_bot, particle_system)

        yellow_ship.update()
        red_ship.update()

        handle_bullets(yellow_bullets, red_bullets, yellow_ship, red_ship, ai_bot, particle_system)

        # Update particle system
        particle_system.update()

        # Draw everything
        WIN.fill(DARK_NAVY)
        draw_starfield()
        draw_border()  # Border is now invisible but still exists for collision

        # Draw spaceships
        yellow_ship.draw(WIN)
        red_ship.draw(WIN)

        # Draw bullets
        draw_bullets(red_bullets, CRIMSON)
        draw_bullets(yellow_bullets, GOLD)

        # Draw particles (minimal)
        particle_system.draw(WIN)

        # Draw UI
        draw_professional_ui(red_health, yellow_health)

        pygame.display.update()

    return None

if __name__ == "__main__":
    while True:
        result = main()
        if result != "menu":
            break