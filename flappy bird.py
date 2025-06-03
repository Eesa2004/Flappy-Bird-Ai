import pygame
import random
from pygame import mixer
import sys

# Constants
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
BIRD_X = 50
BIRD_START_Y = 200
GRAVITY = 0.1
FLAP_VEL = -4.5
FPS = 120

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Load images
bg_image = pygame.transform.scale(
    pygame.image.load("background.png").convert(), (SCREEN_WIDTH, SCREEN_HEIGHT)
)
bird_image = pygame.image.load("bird.png").convert_alpha()
bird_flip_image = pygame.image.load("bird_flip.png").convert_alpha()

# Load sounds
flap_sound = mixer.Sound("flap.wav")
hit_sound = mixer.Sound("hit.wav")
die_sound = mixer.Sound("die.wav")
# Use dedicated channels for prioritization
flap_channel = mixer.Channel(1)
effect_channel = mixer.Channel(2)  # For hit/die, higher priority

# Font
font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()


def death():
    # Immediately stop all lower-priority sounds (including flap)
    flap_channel.stop()
    # Play hit sound with priority, then die sound
    effect_channel.play(hit_sound)
    # Wait for hit to finish, but keep event loop alive to avoid freezing
    hit_len = int(hit_sound.get_length() * 1000)
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < hit_len:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.time.delay(10)
    effect_channel.play(die_sound)
    # Optionally, wait for die sound to finish (non-blocking, but can block if desired)
    # die_len = int(die_sound.get_length() * 1000)
    # start_time = pygame.time.get_ticks()
    # while pygame.time.get_ticks() - start_time < die_len:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #             sys.exit()
    #     pygame.time.delay(10)


def draw_text_center(text, y, color=(255, 255, 255)):
    text_surface = font.render(str(text), True, color)
    screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, y))


def start_screen(bird_y, score):
    start = True
    bird_vel = 0
    while start:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.event.pump()
                flap_channel.stop()
                flap_channel.play(flap_sound, maxtime=150)
                bird_vel = FLAP_VEL
                start = False
        screen.blit(bg_image, (0, 0))
        draw_text_center("PRESS SPACE", 250)
        screen.blit(bird_image, (BIRD_X, bird_y))
        draw_text_center(score, 50)
        pygame.display.update()
    return bird_vel


def game_over_screen(bird_y, bird_vel, score):
    game_over = True
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if bird_y < 480:
            bird_y += bird_vel
            bird_vel += GRAVITY
        screen.blit(bg_image, (0, 0))
        draw_text_center("GAME OVER", 200)
        screen.blit(bird_image, (BIRD_X, bird_y))
        draw_text_center(score, 50)
        pygame.display.update()


def main():
    running = True
    score = 0
    bird_y = BIRD_START_Y
    bird_vel = 0

    # Start screen
    bird_vel = start_screen(bird_y, score)

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.event.pump()
                flap_channel.stop()
                flap_channel.play(flap_sound, maxtime=150)
                bird_vel = FLAP_VEL

        bird_y += bird_vel
        bird_vel += GRAVITY

        # Collision with top or bottom
        if bird_y < 0 or bird_y + bird_image.get_height() > SCREEN_HEIGHT:
            screen.blit(bird_flip_image, (BIRD_X, bird_y))
            pygame.display.update()
            death()
            running = False
            break

        screen.blit(bg_image, (0, 0))
        screen.blit(bird_image, (BIRD_X, bird_y))
        draw_text_center(score, 50)
        pygame.display.update()

    game_over_screen(bird_y, bird_vel, score)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
