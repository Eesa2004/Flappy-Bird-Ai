# Flappy Bird AI

A modern, pygame-powered recreation of Flappy Bird, featuring both human and AI gameplay.  
This project demonstrates my skills in Python, game development, and AI integration.

---

## Features

- **Classic Flappy Bird gameplay** with smooth graphics and sound.
- **Human mode:** Play using the keyboard.
- **AI mode:** Watch an AI agent play the game automatically.
    - **Rule-based AI:** A simple, interpretable agent that navigates pipes by tracking the gap.
    - (Optional) **RL agent:** Easily extensible for reinforcement learning experiments.
- **Clean codebase:** Modular, readable, and extensible Python code.
- **Sound effects and animations** for an authentic experience.

---

## Project Structure

```
flappy-bird/
├── flappy bird.py      # Main game loop and UI
├── RL agent.py         # (Optional) Reinforcement learning agent
├── RB_agent.py         # Rule-based AI agent (default)
├── assets/             # Images and sounds (not included here)
├── README.md           # This file
```

---

## How to Run

1. **Install dependencies:**
    ```bash
    pip install pygame numpy torch
    ```
2. **Add assets:**  
   Place `background.png`, `bird.png`, `bird_flip.png`, `pipe.png`, `flap.wav`, `hit.wav`, `die.wav` in the project directory or `assets/`.

3. **Play the game:**
    ```bash
    python flappy\ bird.py
    ```
    - Type `play` to play yourself.
    - Type `ai` to watch the AI agent play.

---

## AI Integration

- **Rule-based agent:**  
  The AI observes the bird's position and the next pipe's gap, flapping only when below the gap center.  
  This demonstrates effective state extraction and simple control logic.

- **RL agent (optional):**  
  The codebase is structured to allow easy experimentation with reinforcement learning by swapping in `RL agent.py`.

---

## Skills Demonstrated

- **Python & Pygame:**  
  Game loop, event handling, collision detection, animation, and sound.
- **AI Integration:**  
  Modular design for swapping between human, rule-based, and RL agents.
- **Code Quality:**  
  Clean, well-documented, and extensible code.
- **Software Design:**  
  Separation of concerns, reusable functions, and clear project structure.

---

## Future Work

- Improve RL agent performance and training.
- Add visualizations for AI decision-making.
- Experiment with different AI strategies.

---

**Author:**  
Eesa  

