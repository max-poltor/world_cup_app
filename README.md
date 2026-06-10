# FIFA World Cup 2026 Score Logger

A lightweight Streamlit app for friends and colleagues to predict World Cup match scores, compare guesses, and compete on a live leaderboard.

---

## Overview

The app lets a fixed group of users submit scoreline predictions for upcoming World Cup matches. Once official results are in, it automatically scores each prediction and ranks users on a leaderboard. Everything is backed by a SQL database so predictions persist across sessions.

---

## Features

### Log Scores
Each user selects their name from the sidebar and submits score predictions for any match scheduled within the next 7 days. Each form is locked after submission — predictions cannot be changed once entered. Duplicate submissions are prevented both in-session and across sessions via database checks.

### Group Results
Shows the group's consensus prediction for each upcoming match, calculated as the median scoreline across all submitted predictions. Displays the predicted winner (or draw) alongside team flags.

### Leaderboard
Once official match results are recorded in the source data, the leaderboard scores every prediction using the following points system:

| Outcome | Points |
|---|---|
| Exact scoreline | 3 |
| Correct result (win/draw/loss), wrong score | 1 |
| Wrong result | 0 |

Users are ranked by total points accumulated across all played matches.

### All Entries
A raw view of every prediction submitted by all users, useful for transparency and debugging.

---

## Adding Users

User names are currently defined as a static list in the sidebar `selectbox`. To add or remove participants, update the `options` list in `app.py`:

```python
options=['Deborah', 'Bhavna', 'Max']
```