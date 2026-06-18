# Neon Snake Arena — Web Edition (Django)

**GitHub Repository:** https://github.com/S1A8H3I4L/Neon-Snake-Arena

A multiplayer-by-turns Snake game: players enter a name, play in the
browser, and their score is saved to a database. A leaderboard ranks
every player by their best score, and a Django admin panel gives you
full visibility into players, individual game results, and aggregate
statistics.

This is the web rewrite of the original Pygame desktop version —
same core mechanics (grid movement, growth, collision detection,
speed ramp-up), now running in any browser with persistent,
multi-player score tracking.

## Features

- 🎮 Browser-based Snake gameplay
- 👤 Player name registration
- 🏆 Persistent leaderboard rankings
- 💾 Database-backed score storage
- 📊 Game statistics dashboard
- 🔒 Session-based player tracking
- 🎨 Neon-themed arcade-inspired UI
- ⚡ Dynamic speed progression
- 🛡 CSRF-protected score submission
- 🧪 Automated test coverage

## Tech stack

- **Frontend:** HTML + CSS + vanilla JavaScript (Canvas 2D for the game itself — no frontend framework or build step)
- **Backend:** Django 6
- **Database:** SQLite by default (zero setup). A commented PostgreSQL config is included in `snakeweb/settings.py` for production use — swapping it requires no model or view changes.

## Project structure

```
neon_snake_arena/
├── manage.py
├── requirements.txt
├── snakeweb/              # Django project config
│   ├── settings.py
│   └── urls.py
├── game/                  # The game app
│   ├── models.py          # Player, Score
│   ├── views.py           # home, start_game, play, save_score (API), leaderboard
│   ├── admin.py            # Admin registration + Game Statistics dashboard
│   ├── urls.py
│   ├── tests.py            # 15 automated tests covering the full flow
│   └── templates/
│       ├── game/
│       │   ├── home.html         # Name entry
│       │   ├── play.html         # Game canvas
│       │   └── leaderboard.html  # Top players table
│       └── admin/
│           └── game_statistics.html
└── static/
    ├── css/neon.css        # Shared neon design system
    └── js/snake_game.js    # Game engine (Canvas 2D)
```

## How it works

1. **Name entry** (`/`) — player types a name and submits. The name is
   stored against a `Player` row (reused if the same name plays again,
   so score history accumulates) and saved in the session.
2. **Play** (`/play/`) — a canvas-based Snake game. Arrow keys move,
   `P` pauses, the snake grows on eating food, and speed increases
   every 4 foods eaten. Hitting a wall or itself ends the game.
3. **Game over** — the final score is POSTed to `/api/save-score/` as
   JSON, validated server-side, and saved as a new `Score` row linked
   to the player. The page shows "Saved Successfully" along with the
   player's rank.
4. **Leaderboard** (`/leaderboard/`) — shows each player's *best*
   score (not every individual game), ranked highest first.
5. **Admin panel** (`/admin/`) — manage `Players` and `Scores`
   directly, plus a read-only `Game Statistics` dashboard showing
   total players, total games played, the top score ever, and the
   average score across all games.

## Setup

```bash
# 1. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up the database
python manage.py migrate

# 4. Create an admin account
python manage.py createsuperuser

# 5. Run the development server
python manage.py runserver
```

Then open `http://127.0.0.1:8000/` in your browser to play, and
`http://127.0.0.1:8000/admin/` to manage data.

## Running the tests

```bash
python manage.py test game
```

This runs 15 tests covering: name validation, session handling,
score persistence, duplicate-name reuse, leaderboard ranking, and
admin panel registration.

## Notes on design choices

- **Best score per player on the leaderboard, not every game.** This
  matches the brief's example output and stops one player from
  flooding the board with repeated low scores. Full per-game history
  is still kept in the `Score` table and visible in the admin panel
  (and via each player's inline score list).
- **Sessions, not client-supplied player IDs.** The score-saving
  endpoint trusts the Django session (set when the name form is
  submitted) rather than trusting a player ID sent from the browser,
  so one player can't submit scores under another player's name by
  editing a request.
- **CSRF protection is kept on**, including for the AJAX score-save
  call — the token is read from Django's template context and sent
  as a header, rather than disabling protection to make the fetch
  call easier.

## Author

### Sahil Panchal

Neon Snake Arena is a full-stack Django web application developed to demonstrate modern web development, game logic implementation, database integration, session management, leaderboard systems, and interactive browser-based gameplay.

### Skills Demonstrated

- Python Development
- Django Web Framework
- Database Design & ORM
- HTML5 Canvas Game Development
- JavaScript Programming
- Session & State Management
- Leaderboard & Ranking Systems
- REST-style API Development
- Frontend UI/UX Design
- Software Testing & Debugging

### Project Highlights

- Persistent player profiles and score history
- Dynamic leaderboard with best-score ranking
- Secure score submission with CSRF protection
- Django admin analytics dashboard
- Responsive neon-themed user interface
- Browser-based arcade gaming experience

---

Built with ❤️ using Django, Python, JavaScript, HTML5, CSS3, and SQLite.