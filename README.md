# 🚀 Quantum Clash: AI Reign

**Quantum Clash: AI Reign** is a fast-paced, arcade-style 2D spaceship combat game built using Python and Pygame. Engage in thrilling 1v1 battles against a smart AI bot or another player in a galactic arena.

---

## 🎮 Features

* ✨ **Stylish Animated Main Menu** with glowing buttons and background effects
* 🌌 **Two Game Modes**: Player vs Player and Player vs AI Bot
* ⚔️ **Dynamic Combat Mechanics** with health tracking, shooting, and evasion
* 💥 **Particle Effects** for bullet impacts and exhaust trails
* 🌟 **AI Difficulty System**: Bot behavior changes based on difficulty level
* 🌋 **Professional UI** with health bars, player names, and match summary screens

---

## 📂 Project Structure

```bash
/galaxy-fighters
|
|├── Assets/           # (Optional) Add custom spaceship images or sounds
|├── game.py            # Main game logic (1v1 with AI bot)
|├── main_menu.py       # Animated main menu UI
|└── run.py             # Entry point that launches the main menu
```

> The game runs without any assets by default. To enhance visuals or sounds, you can optionally place custom spaceship images and sound effects in the **Assets/** folder.

---

## 🔧 How to Run

### Requirements:

* Python 3.8+
* `pygame` library

### Install dependencies:

```bash
pip install pygame
```

### Run the Game:

```bash
python run.py
```

---

## 🔠 Controls

### Player (Right Side - Red)

* `Arrow Keys` to move
* `Space` to shoot

### AI Bot (Left Side - Yellow)

* Automatically moves, dodges bullets, and fires based on difficulty

---

## 🎖️ Game Flow

1. Launch the game with `run.py`
2. Navigate through the **animated main menu**
3. Choose **"Start Mission"** to enter combat
4. Defeat your opponent before your health runs out
5. At the end screen:

   * Press `R` to restart
   * Press `M` to return to menu
   * Press `Esc` to exit

---

## 🌟 Credits

Built with love using [Pygame](https://www.pygame.org/)
Art & sound are optional and can be customized using the **Assets/** folder.

---

## 🛡️ License

MIT License. Free to modify and use for personal or educational projects.

---

Made by ALAAP — Defend the Galaxy 
