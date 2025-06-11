import pygame
import math
import random
from game import main as main

WIDTH = 900
HEIGHT = 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

def draw_stars(surface, stars):
    # <Content unchanged...>
    for star in stars:
        brightness = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01 + star[2]))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (int(star[0]), int(star[1])), 1)

def draw_nebula_effect(surface, time_offset):
    # <Content unchanged...>
    for i in range(5):
        alpha = int(30 + 20 * math.sin(time_offset * 0.002 + i))
        color = [
            max(0, min(255, 80 + int(30 * math.sin(time_offset * 0.001 + i)))),   # corrected line
            max(0, min(255, 20 + int(40 * math.sin(time_offset * 0.0015 + i)))),  # corrected line
            max(0, min(255, 120 + int(50 * math.sin(time_offset * 0.0008 + i))))  # corrected line
        ]
        color = tuple(max(0, min(255, c)) for c in color)

        nebula_surface = pygame.Surface((200, 150))
        nebula_surface.set_alpha(alpha)
        nebula_surface.fill(color)
        x = WIDTH // 2 + int(100 * math.sin(time_offset * 0.0005 + i)) - 100
        y = HEIGHT // 2 + int(80 * math.cos(time_offset * 0.0007 + i)) - 75
        surface.blit(nebula_surface, (x, y))

def draw_futuristic_button(surface, rect, text, font, hover, glow_intensity=0):
    # <Content unchanged...>
    if hover or glow_intensity > 0:
        glow_color = (0, 150, 255) if not hover else (255, 100, 0)
        glow_alpha = int(50 + glow_intensity * 30) if not hover else 80
        for i in range(3, 0, -1):
            glow_rect = rect.inflate(i * 8, i * 8)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height))
            glow_surf.set_alpha(glow_alpha // i)
            glow_surf.fill(glow_color)
            surface.blit(glow_surf, glow_rect.topleft)
    button_color = (30, 30, 60) if not hover else (60, 30, 30)
    border_color = (100, 150, 255) if not hover else (255, 100, 0)
    pygame.draw.rect(surface, button_color, rect)
    pygame.draw.rect(surface, border_color, rect, 2)
    highlight_rect = rect.inflate(-4, -4)
    pygame.draw.rect(surface, (255, 255, 255, 30), highlight_rect, 1)
    text_color = (200, 220, 255) if not hover else (255, 200, 150)
    rendered_text = font.render(text, True, text_color)
    text_rect = rendered_text.get_rect(center=rect.center)
    surface.blit(rendered_text, text_rect)

def main_menu():
    title_font = pygame.font.SysFont('arial', 80, bold=True)
    subtitle_font = pygame.font.SysFont('arial', 24)
    menu_font = pygame.font.SysFont('arial', 32, bold=True)

    stars = []
    for _ in range(150):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        twinkle_offset = random.uniform(0, math.pi * 2)
        stars.append([x, y, twinkle_offset])

    click = False
    start_time = pygame.time.get_ticks()
    while True:
        current_time = pygame.time.get_ticks()
        time_since_start = current_time - start_time

        WIN.fill((5, 5, 15))
        draw_nebula_effect(WIN, time_since_start)
        draw_stars(WIN, stars)

        title_glow = 1 + 0.3 * math.sin(time_since_start * 0.005)
        r = min(255, int(150 + 100 * title_glow))
        g = min(255, int(200 + 50 * title_glow))
        b = 255
        title_color = (r, g, b)
        for offset in range(3, 0, -1):
            glow_surface = pygame.Surface((WIDTH, 100))
            glow_surface.set_alpha(30)
            glow_text = title_font.render("QUANTUM CLASH", True, title_color)
            glow_rect = glow_text.get_rect(center=(WIDTH // 2 + offset, 100 + offset))
            WIN.blit(glow_text, glow_rect)
        title_text = title_font.render("QUANTUM CLASH", True, title_color)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
        WIN.blit(title_text, title_rect)

        subtitle = "Defend the Galaxy"
        visible_chars = int((time_since_start % 3000) / 100)
        if visible_chars > len(subtitle):
            visible_chars = len(subtitle)
        subtitle_text = subtitle_font.render(subtitle[:visible_chars], True, (180, 180, 220))
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, 140))
        WIN.blit(subtitle_text, subtitle_rect)

        mx, my = pygame.mouse.get_pos()
        button_start = pygame.Rect(WIDTH // 2 - 120, 220, 240, 60)
        button_quit = pygame.Rect(WIDTH // 2 - 120, 300, 240, 60)
        draw_futuristic_button(WIN, button_start, "START MISSION", menu_font, button_start.collidepoint((mx, my)))
        draw_futuristic_button(WIN, button_quit, "ABORT MISSION", menu_font, button_quit.collidepoint((mx, my)))
        scan_y = (time_since_start // 10) % HEIGHT
        for i in range(3):
            line_alpha = 30 - i * 10
            scan_surface = pygame.Surface((WIDTH, 2))
            scan_surface.set_alpha(line_alpha)
            scan_surface.fill((0, 255, 150))
            WIN.blit(scan_surface, (0, scan_y + i * 2))
        hud_color = (0, 255, 150)
        pygame.draw.lines(WIN, hud_color, False, [(20, 20), (20, 60), (60, 60)], 2)
        pygame.draw.lines(WIN, hud_color, False, [(WIDTH-60, 60), (WIDTH-20, 60), (WIDTH-20, 20)], 2)
        pygame.draw.lines(WIN, hud_color, False, [(60, HEIGHT-60), (20, HEIGHT-60), (20, HEIGHT-20)], 2)
        pygame.draw.lines(WIN, hud_color, False, [(WIDTH-20, HEIGHT-20), (WIDTH-20, HEIGHT-60), (WIDTH-60, HEIGHT-60)], 2)
        if click:
            if button_start.collidepoint((mx, my)):
                main()  # <-- Call your spaceship AI logic
            if button_quit.collidepoint((mx, my)):
                pygame.quit()
                exit()
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()

if __name__ == "__main__":
    pygame.init()
    try:
        main_menu()
    except Exception as e:
        print("Error:", e)
        input("Press Enter to exit...")