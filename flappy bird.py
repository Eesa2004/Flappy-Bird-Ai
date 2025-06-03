import pygame
import random
from pygame import mixer
import sys

# Constants
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
BIRD_X = 50
BIRD_START_Y = 200
GRAVITY = 0.08
FLAP_VEL = -2.5
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
pipe_image = pygame.image.load("pipe.png").convert_alpha()
pipe_image_flipped = pygame.transform.flip(pipe_image, False, True)

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


def create_pipe():
    # Traditional Flappy Bird: each pipe is random, gap is always the same size, gap appears at random y
    gap = 180
    min_pipe_height = 60
    max_pipe_height = SCREEN_HEIGHT - gap - 60
    top_height = random.randint(min_pipe_height, max_pipe_height)
    bottom_y = top_height + gap
    return {
        "x": SCREEN_WIDTH,
        "top_height": top_height,
        "bottom_y": bottom_y,
        "passed": False,
    }


def draw_pipes(pipes):
    PIPE_THIN_WIDTH = (
        36  # Make pipes thinner (original is usually 52px, try 32-40 for thin)
    )
    for pipe in pipes:
        # Top pipe: stretch to top_height, flip, and align bottom with top_height
        top_pipe_img = pygame.transform.scale(
            pipe_image_flipped, (PIPE_THIN_WIDTH, int(pipe["top_height"]))
        )
        screen.blit(
            top_pipe_img,
            (pipe["x"], 0),
        )
        # Bottom pipe: stretch to fill from bottom_y to bottom, align bottom with screen
        bottom_pipe_height = SCREEN_HEIGHT - pipe["bottom_y"]
        bottom_pipe_img = pygame.transform.scale(
            pipe_image, (PIPE_THIN_WIDTH, int(bottom_pipe_height))
        )
        screen.blit(
            bottom_pipe_img,
            (pipe["x"], pipe["bottom_y"]),
        )


def check_collision(bird_rect, pipes):
    PIPE_THIN_WIDTH = 36
    for pipe in pipes:
        # Top pipe rect
        top_pipe_rect = pygame.Rect(pipe["x"], 0, PIPE_THIN_WIDTH, pipe["top_height"])
        # Bottom pipe rect
        bottom_pipe_rect = pygame.Rect(
            pipe["x"],
            pipe["bottom_y"],
            PIPE_THIN_WIDTH,
            SCREEN_HEIGHT - pipe["bottom_y"],
        )
        if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(
            bottom_pipe_rect
        ):
            return True
    return False


def main():
    running = True
    score = 0
    bird_y = BIRD_START_Y
    bird_vel = 0

    # Pipe variables
    pipes = [create_pipe()]
    pipe_speed = 1.2
    pipe_spawn_timer = 0
    pipe_spawn_interval = 1400  # ms

    # Start screen
    bird_vel = start_screen(bird_y, score)

    last_time = pygame.time.get_ticks()

    while running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        dt = now - last_time
        last_time = now

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

        # Pipes movement and generation
        pipe_spawn_timer += dt
        if pipe_spawn_timer > pipe_spawn_interval:
            pipes.append(create_pipe())
            pipe_spawn_timer = 0

        for pipe in pipes:
            pipe["x"] -= pipe_speed

        # Remove pipes that have gone off screen
        PIPE_THIN_WIDTH = 36
        pipes = [pipe for pipe in pipes if pipe["x"] > -PIPE_THIN_WIDTH]

        # Bird rect for collision (smaller hitbox)
        hitbox_margin_x = 6
        hitbox_margin_y = 6
        bird_rect = pygame.Rect(
            BIRD_X + hitbox_margin_x,
            int(bird_y) + hitbox_margin_y,
            bird_image.get_width() - 2 * hitbox_margin_x,
            bird_image.get_height() - 2 * hitbox_margin_y,
        )

        # Collision with pipes
        if check_collision(bird_rect, pipes):
            screen.blit(bird_flip_image, (BIRD_X, bird_y))
            pygame.display.update()
            death()
            running = False
            break

        # Collision with top or bottom
        if bird_y < 0 or bird_y + bird_image.get_height() > SCREEN_HEIGHT:
            screen.blit(bird_flip_image, (BIRD_X, bird_y))
            pygame.display.update()
            death()
            running = False
            break

        # Score update
        PIPE_THIN_WIDTH = 36
        for pipe in pipes:
            if not pipe["passed"] and pipe["x"] + PIPE_THIN_WIDTH < BIRD_X:
                pipe["passed"] = True
                score += 1

        screen.blit(bg_image, (0, 0))
        draw_pipes(pipes)
        screen.blit(bird_image, (BIRD_X, bird_y))
        draw_text_center(score, 50)
        pygame.display.update()

    game_over_screen(bird_y, bird_vel, score)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
