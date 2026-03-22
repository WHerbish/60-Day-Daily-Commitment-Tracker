# 60-Day Daily Commitment Tracker

A Python-based, locally-hosted web app for building habits through daily commitment across a 60-day period. Track your consistency and watch your progress fill in one block at a time.

---

## Inspiration

- **[HabitKit](https://www.habitkit.app/)**
- **Twitch Streamer Atrioc's 60-Day Commitment Tracker**

This project was also built as an experiment in **vibe-coding with [Claude](https://claude.ai/claude-code)**.

---

## Features

- Create multiple tasks, with custom colour options.
- 60-Day grid per task, with one block per day, starting from the day the task was created.
- Daily "Check" button to mark today's task having been achieved.
- Blocks from previous days are permanently locked to their complete/incomplete status, creating an honesty history.
- Tasks can be renamed (click the title to edit, just like renaming a file on MacOS).
- Personalised greeting based on time of day upon login.
- All data stored locally under `src/resources/config.json`. 

---

## Requirements

- Python 3.7+
- Flask

Install Flask via pip if you don't have it:

```bash
pip install flask
```

---

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/your-username/60-Day-Daily-Commitment-Tracker.git
cd 60-Day-Daily-Commitment-Tracker
```

2. Run the app:

```bash
python src/main/main.py
```

The app can also be ran via the DailyCommitmentTracker.command executable.

3. The app will open automatically in your browser at `http://localhost:8080`.

---

## Project Structure

```
60-Day-Daily-Commitment-Tracker/
├── src/
│   ├── main/
│   │   └── main.py          # Flask app — all routes and UI
│   └── resources/
│       └── config.json      # Local data store (git-ignored)
│       └── colours.png      # Colours used to lable different tasks
├── .gitignore
├── DailyCommitmentTracker.command
├── LICENSE
├── pyproject.toml
└── README.md
```

---

## Notes

- `config.json` is excluded from version control. Your personal task data stays on your machine.
- The app is intended to run locally, to be deployed to a server.