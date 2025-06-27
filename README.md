# ChessTutor – Local AI-Assisted Chess Coach

This project is a self-contained desktop tutor written in Python + Pygame.  It shows a board, lets you pick curated start positions, and (optionally) connects to a chess engine and OpenAI for coaching.

---
## 1. Quick Start (macOS / Linux / Windows)

```bash
# 1 – clone & enter
git clone https://github.com/you/chessTutor.git
cd chessTutor

# 2 – create Python 3.12+ environment
#    (pick ONE of the following)
# ➜ Conda
conda create -n tutorchess python=3.12 -y
conda activate tutorchess
# ➜ venv
python -m venv .venv
source .venv/bin/activate      # (Windows: .venv\Scripts\activate)

# 3 – install Python deps
pip install -r requirements.txt

# 4 – install native Cairo libs  ••• IMPORTANT ••• (cross-platform)
conda install -c conda-forge cairo pango gdk-pixbuf cairosvg

# 5 – (optional) Stockfish engine for strong play
brew install stockfish                # macOS
sudo apt-get install stockfish        # Linux
choco install stockfish               # Windows
# or download binary & add to PATH

# 6 – run the tutor
python main.py
```

---
## 2. Controls & Features

1. **Start-Position Menu (console)**  – enter a number (1-80) to load themed practice positions (openings, tactics, endgames…).
2. **Board Interaction**
   * Left-click a piece, then left-click a destination
   * Green dots show legal targets.
3. **Opponent Strength**  – by default uses Stockfish (if present) at skill 10, otherwise a depth-2 minimax.
4. **In-game Shortcuts** *(coming in commit 3)*
   * `F2` – open graphical category picker without restarting.
   * `Esc` – back out of menus.
5. **Quit**  – close window or press `Ctrl+W`.

---
## 3. Environment Variables

| Variable           | Purpose                                       | Example                |
|--------------------|-----------------------------------------------|------------------------|
| `STOCKFISH_PATH`   | Path to Stockfish binary (if not in `PATH`)    | `/usr/local/bin/stockfish` |
| `OPENAI_API_KEY`   | Enables LLM tips / Q&A (future milestone)     | `sk-...`               |
| `OPENAI_MODEL`     | Override default model                        | `gpt-4o`               |

Set them in your shell or a `.env` file (with [python-dotenv] if you prefer).

---
## 4. Troubleshooting

* **`OSError: no library called "cairo" was found`**  → install native Cairo libraries (step 4 above) and restart the Python process.
* **Pieces / icons invisible**  → ensure `cairosvg` rendered correctly; try deleting `__pycache__` and rerun.
* **No sound (future TTS)**  → install `pyttsx3` + system voices.

---
## 5. Project Layout (after commit 3)

```
chessTutor/
├── icons/               # SVG category icons
├── pieces_svg/          # Staunton SVG piece set
├── start_positions.json # 80 practice positions
├── gfx.py               # SVG → Surface helper
├── menu.py              # graphical picker (commit 3)
├── main.py              # game loop
└── requirements.txt
```

---
## 6. Contributing

PRs welcome—especially for:
* Additional start positions with kid-friendly descriptions.
* Better SVG icons.
* Language localisation.

---
*Happy tutoring!* 