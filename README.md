# Share the Load

A calm, minimal Streamlit app that helps couples see and rebalance the mental load of running a household.

**📱 Want it on your iPhones?** Follow [DEPLOY.md](./DEPLOY.md) — about 15 minutes, free, ends with an app icon on both phones that syncs between you.

## Design principles
- **Calm palette** — sage and warm sand on an off-white background; one accent per chart
- **State first, list second** — opening the app shows *the state of the household*, not a wall of tasks
- **Gentle, not gamified** — suggestions instead of alerts, appreciation instead of streaks
- **Privacy** — data stays on your own infrastructure (local file or your own Supabase project)

## Features
- Two-minute guided onboarding (names → swipe through default tasks → done)
- Curated 29-task library across Food, Home, Kids, Admin, Planning, Emotional
- Per-task **mental-load weight (1–10)** that you can tune
- **Invisible work** flag — the dashboard tells you what % of the load is invisible
- Owners can be a partner, **Shared**, or **Unassigned**
- **Transfer** a task to your partner with a short message
- **Appreciation** notes — a quiet space for thanks
- **Weekly rhythm** — pause tasks for the week or start a fresh week
- **Smart suggestion** — when the balance tips, names a specific task to share
- **Cloud sync** between phones via free Supabase (optional)
- iOS-friendly: meta tags, safe-area padding, 44px tap targets, fullscreen when added to Home Screen

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to your iPhones
See [DEPLOY.md](./DEPLOY.md).

## Files
- `app.py` — the Streamlit app
- `storage.py` — Supabase + local-file storage layer
- `requirements.txt` — Python deps
- `.streamlit/config.toml` — theme + minimal toolbar
- `.streamlit/secrets.toml.example` — template for Supabase keys
- `DEPLOY.md` — full deploy + sync + Add-to-Home-Screen guide
