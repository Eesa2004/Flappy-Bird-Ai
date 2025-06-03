# --- SIMPLE RULE-BASED AI AGENT ---

import numpy as np

def get_state(bird_y, bird_vel, pipes):
    # Find the next pipe in front of the bird
    PIPE_THIN_WIDTH = 36
    next_pipe = None
    for pipe in pipes:
        if pipe["x"] + PIPE_THIN_WIDTH > BIRD_X:
            next_pipe = pipe
            break
    if next_pipe is None:
        next_pipe = pipes[0]
    pipe_x = next_pipe["x"]
    pipe_gap_y = next_pipe["top_height"] + 90  # center of the gap
    return bird_y, pipe_gap_y

def simple_ai_action(bird_y, pipe_gap_y):
    # Flap if bird is below the gap center, else do nothing
    if bird_y > pipe_gap_y:
        return 1  # flap
    else:
        return 0  # do nothing

def run_episode(policy_net=None, epsilon=0.0, train=False):
    score = 0
    bird_y = BIRD_START_Y
    bird_vel = 0
    pipes = [create_pipe()]
    pipe_speed = 1.2
    pipe_spawn_timer = 0
    pipe_spawn_interval = 1400
    last_time = pygame.time.get_ticks()
    running = True
    PIPE_THIN_WIDTH = 36

    while running:
        now = pygame.time.get_ticks()
        dt = now - last_time
        last_time = now

        # --- Simple AI chooses action ---
        bird_y_state, pipe_gap_y = get_state(bird_y, bird_vel, pipes)
        action = simple_ai_action(bird_y_state, pipe_gap_y)

        # --- Apply action ---
        if action == 1:
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
            running = False

        # Collision with top or bottom
        if bird_y < 0 or bird_y + bird_image.get_height() > SCREEN_HEIGHT:
            running = False

        # Score update
        for pipe in pipes:
            if not pipe.get("passed", False) and pipe["x"] + PIPE_THIN_WIDTH < BIRD_X:
                pipe["passed"] = True
                score += 1

        # --- Draw (for watching agent) ---
        if not train:
            screen.blit(bg_image, (0, 0))
            draw_pipes(pipes)
            screen.blit(bird_image, (BIRD_X, bird_y))
            draw_text_center(score, 50)
            pygame.display.update()
            clock.tick(60)

    return score, 0  # total_reward not used

def train_agent(num_episodes=1):
    # No training needed for rule-based agent
    print("Rule-based agent does not require training.")
    return None

def watch_agent(policy_net=None, num_episodes=5):
    for i in range(num_episodes):
        print(f"Watching episode {i+1}")
        run_episode(train=False)
        pygame.time.wait(1000)

if __name__ == "__main__":
    mode = input("Type 'ai' to watch AI, 'play' to play yourself: ").strip().lower()
    if mode == "ai":
        print("Watching the rule-based agent play...")
        watch_agent(num_episodes=3)
        pygame.quit()
        sys.exit()
    else:
        main()
