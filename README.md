# Share the Load

A calm, minimal Streamlit app that helps couples see and rebalance the mental load of running a household.

## Design principles
- **Calm palette** — sage and warm sand on an off-white background; one accent per chart
- **State first, list second** — opening the app shows *the state of the household*, not a wall of tasks
- **Gentle, not gamified** — suggestions instead of alerts, appreciation instead of streaks
- **Privacy** — all data stays on the local device as a JSON file

## Features
- Two-minute guided onboarding (names → swipe through default tasks → done)
- Curated 29-task library across Food, Home, Kids, Admin, Planning, Emotional
- Per-task **mental-load weight (1–10)** that you can tune
- **Invisible work** flag — the dashboard tells you what % of the load is invisible
- Owners can be a partner, **Shared**, or **Unassigned**
- **Transfer** a task to your partner with a short message
- **Appreciation** notes — a quiet space for thanks, separate from notes
- **Weekly rhythm** — pause tasks for the week or start a fresh week from Settings
- **Smart suggestion** — when the balance tips, the app names a specific task to share
- Save / download / restore data as JSON

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Push to GitHub, then connect at [share.streamlit.io](https://share.streamlit.io). Main file: `app.py`.
