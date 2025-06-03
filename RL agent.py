# --- RL AGENT ---

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import collections

# --- RL Hyperparameters ---
STATE_SIZE = 4  # [bird_y, bird_vel, pipe_x - bird_x, pipe_gap_y - bird_y]
ACTION_SIZE = 2  # 0: do nothing, 1: flap
GAMMA = 0.99
LR = 1e-3
MEMORY_SIZE = 10000
BATCH_SIZE = 64
EPS_START = 1.0
EPS_END = 0.01
EPS_DECAY = 0.995

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_size),
        )

    def forward(self, x):
        return self.net(x)


class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)

    def push(self, *args):
        self.buffer.append(tuple(args))

    def sample(self, batch_size):
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        batch = [self.buffer[idx] for idx in indices]
        return map(np.array, zip(*batch))

    def __len__(self):
        return len(self.buffer)


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
    return np.array(
        [
            bird_y / SCREEN_HEIGHT,
            bird_vel / 10.0,
            (pipe_x - BIRD_X) / SCREEN_WIDTH,
            (pipe_gap_y - bird_y) / SCREEN_HEIGHT,
        ],
        dtype=np.float32,
    )


def run_episode(policy_net, epsilon, train=True):
    score = 0
    bird_y = BIRD_START_Y
    bird_vel = 0
    pipes = [create_pipe()]
    pipe_speed = 1.2
    pipe_spawn_timer = 0
    pipe_spawn_interval = 1400
    last_time = pygame.time.get_ticks()
    running = True
    total_reward = 0
    PIPE_THIN_WIDTH = 36

    while running:
        now = pygame.time.get_ticks()
        dt = now - last_time
        last_time = now

        # --- RL agent chooses action ---
        state = get_state(bird_y, bird_vel, pipes)
        if train and np.random.rand() < epsilon:
            action = np.random.randint(ACTION_SIZE)
        else:
            with torch.no_grad():
                qvals = policy_net(torch.tensor(state, device=device).unsqueeze(0))
                action = int(torch.argmax(qvals).item())

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

        # --- Reward shaping ---
        reward = 0.1  # small reward for staying alive

        # Collision with pipes
        if check_collision(bird_rect, pipes):
            reward = -1.0
            running = False

        # Collision with top or bottom
        if bird_y < 0 or bird_y + bird_image.get_height() > SCREEN_HEIGHT:
            reward = -1.0
            running = False

        # Score update
        for pipe in pipes:
            if not pipe["passed"] and pipe["x"] + PIPE_THIN_WIDTH < BIRD_X:
                pipe["passed"] = True
                score += 1
                reward = 1.0  # reward for passing a pipe

        total_reward += reward

        # --- RL: store transition ---
        if train:
            next_state = get_state(bird_y, bird_vel, pipes)
            done = not running
            replay_buffer.push(state, action, reward, next_state, done)

        # --- Draw (optional, for watching agent) ---
        if not train:
            screen.blit(bg_image, (0, 0))
            draw_pipes(pipes)
            screen.blit(bird_image, (BIRD_X, bird_y))
            draw_text_center(score, 50)
            pygame.display.update()
            clock.tick(60)

    return score, total_reward


def optimize_model(policy_net, target_net, optimizer, replay_buffer):
    if len(replay_buffer) < BATCH_SIZE:
        return
    states, actions, rewards, next_states, dones = replay_buffer.sample(BATCH_SIZE)
    states = torch.tensor(states, dtype=torch.float32, device=device)
    actions = torch.tensor(actions, dtype=torch.int64, device=device).unsqueeze(1)
    rewards = torch.tensor(rewards, dtype=torch.float32, device=device).unsqueeze(1)
    next_states = torch.tensor(next_states, dtype=torch.float32, device=device)
    dones = torch.tensor(dones, dtype=torch.float32, device=device).unsqueeze(1)

    q_values = policy_net(states).gather(1, actions)
    with torch.no_grad():
        max_next_q = target_net(next_states).max(1)[0].unsqueeze(1)
        target = rewards + GAMMA * max_next_q * (1 - dones)
    loss = nn.MSELoss()(q_values, target)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()


def train_agent(num_episodes=500):
    policy_net = DQN(STATE_SIZE, ACTION_SIZE).to(device)
    target_net = DQN(STATE_SIZE, ACTION_SIZE).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    optimizer = optim.Adam(policy_net.parameters(), lr=LR)
    global replay_buffer
    replay_buffer = ReplayBuffer(MEMORY_SIZE)
    epsilon = EPS_START
    scores = []
    for episode in range(num_episodes):
        score, total_reward = run_episode(policy_net, epsilon, train=True)
        scores.append(score)
        epsilon = max(EPS_END, epsilon * EPS_DECAY)
        optimize_model(policy_net, target_net, optimizer, replay_buffer)
        if episode % 10 == 0:
            target_net.load_state_dict(policy_net.state_dict())
        if episode % 20 == 0:
            print(
                f"Episode {episode}, Score: {score}, Epsilon: {epsilon:.3f}, AvgScore(20): {np.mean(scores[-20:]):.2f}"
            )
    return policy_net


def watch_agent(policy_net, num_episodes=5):
    for i in range(num_episodes):
        print(f"Watching episode {i+1}")
        run_episode(policy_net, epsilon=0.0, train=False)
        pygame.time.wait(1000)


if __name__ == "__main__":
    mode = input("Type 'ai' to train AI, 'play' to play yourself: ").strip().lower()
    if mode == "ai":
        print("Training AI agent (this may take a few minutes)...")
        trained_policy = train_agent(num_episodes=300)
        print("Training complete! Watching the agent play...")
        watch_agent(trained_policy, num_episodes=3)
        pygame.quit()
        sys.exit()
    else:
        main()
