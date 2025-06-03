import pygame
import random
from pygame import mixer
import time
import sys

running = True
start = True
game_over = True

# initialize pygame
pygame.init()
pygame.mixer.init()

# set the screen dimensions
screen_width = 288
screen_height = 512
screen = pygame.display.set_mode((screen_width, screen_height))

# set the title of the window
pygame.display.set_caption("Flappy Bird")

# load the background image and scale it to fit the screen
bg_image = pygame.image.load("background.png").convert()
bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
bg_image_x = 0

# load the bird image and set its initial position
bird_image = pygame.image.load("bird.png").convert_alpha()
bird_x = 50
bird_y = 200

# load the pipe images and set their initial positions
# pipe_image = pygame.image.load("pipe.png").convert_alpha()
# pipe_gap = 100
# pipe_x = screen_width
# pipe1_height = random.randint(100, screen_height - pipe_gap - 100)
# pipe2_height = screen_height - pipe_gap - pipe1_height
# pipe1_y = 0
# pipe2_y = pipe1_height + pipe_gap

# set the bird's initial velocity and gravity
bird_vel = 0
gravity = 0.00009

# set the font for game
font = pygame.font.Font(None, 36)

# set the initial score
score = 0


# sound when you die:
def death():
    hit = mixer.Sound("hit.wav")
    hit.play()
    time.sleep(0.2)
    die = mixer.Sound("die.wav")
    die.play()


clock = pygame.time.Clock()

# start loop
while start:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            game_over = False
            start = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                flap = mixer.Sound("flap.wav")
                flap.play()
                bird_vel = -0.1
                start = False

    # draw the background
    screen.blit(bg_image, (0, 0))

    # draw the pipes
    # screen.blit(pipe_image, (pipe_x, pipe1_y - pipe_image.get_height()))
    # screen.blit(pipe_image, (pipe_x, pipe2_y))

    # draw "Press space to start"
    start_text = font.render(str("PRESS SPACE"), True, (255, 255, 255))
    screen.blit(start_text, (screen_width // 2 - start_text.get_width() // 2, 250))

    # draw the bird
    screen.blit(bird_image, (bird_x, bird_y))

    # draw the score
    score_text = font.render(str(score), True, (255, 255, 255))
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 50))

    # update the screen
    pygame.display.update()


# game loop
while running:

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            game_over = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                flap = mixer.Sound("flap.wav")
                flap.play()
                bird_vel = -0.1

    # move the bird
    bird_y += bird_vel
    bird_vel += gravity

    # move the pipes
    # pipe_x -= 0.06
    # if pipe_x < -pipe_image.get_width():
    #     pipe_x = screen_width
    #     pipe1_height = random.randint(100, screen_height - pipe_gap - 100)
    #     pipe2_height = screen_height - pipe_gap - pipe1_height
    #     pipe1_y = 0
    #     pipe2_y = pipe1_height + pipe_gap

    # # check for collision with pipes
    # if bird_x + bird_image.get_width() > pipe_x and bird_x < pipe_x + pipe_image.get_width():
    #     if bird_y < pipe1_height or bird_y + bird_image.get_height() > pipe2_y:
    #         hit = mixer.Sound("hit.wav")
    #         hit.play()
    #         die = mixer.Sound("die.wav")
    #         die.play()
    #         running = False

    # check for collision with top or bottom of screen
    if bird_y < 0 or bird_y + bird_image.get_height() > screen_height:
        bird_image = pygame.image.load("bird_flip.png").convert_alpha()
        screen.blit(bird_image, (bird_x, bird_y))
        pygame.display.update()
        death()
        running = False

    # update the score
    # if pipe_x == 50:
    #     score += 1

    # draw the background
    # Remove scrolling logic if not needed, or keep for effect
    # bg_image_x -= 0.001
    # if bg_image_x <= -bg_image.get_width():
    #     bg_image_x = 0

    # Draw background to fit the screen (no scrolling)
    screen.blit(bg_image, (0, 0))
    # If you want seamless scrolling, use the scaled image:
    # screen.blit(bg_image, (bg_image_x, 0))
    # screen.blit(bg_image, (bg_image_x + bg_image.get_width(), 0))

    # draw the pipes
    # screen.blit(pipe_image, (pipe_x, pipe1_y - pipe_image.get_height()))
    # screen.blit(pipe_image, (pipe_x, pipe2_y))

    # draw the bird
    screen.blit(bird_image, (bird_x, bird_y))

    # draw the score
    score_text = font.render(str(score), True, (255, 255, 255))
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 50))

    # update the screen
    pygame.display.update()


while game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = False

    # move the bird
    if bird_y < 480:
        bird_y += bird_vel
        bird_vel += gravity

    screen.blit(bg_image, (0, 0))

    # draw "GAME OVER"
    game_over_text = font.render(str("GAME OVER"), True, (255, 255, 255))
    screen.blit(
        game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 200)
    )

    # draw the pipes
    # screen.blit(pipe_image, (pipe_x, pipe1_y - pipe_image.get_height()))
    # screen.blit(pipe_image, (pipe_x, pipe2_y))

    # draw the bird
    screen.blit(bird_image, (bird_x, bird_y))

    # draw the score
    score_text = font.render(str(score), True, (255, 255, 255))
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 50))

    # update the screen
    pygame.display.update()


# quit pygame
pygame.quit()
sys.exit()
