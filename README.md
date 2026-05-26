# 🤝 Share the Load

A friendly Streamlit app to help couples **see, share, and rebalance the mental load** of running a household.

## What it does
- Onboard both partners with their names
- Pick from a curated list of household tasks (cooking, cleaning, kids, admin, planning, emotional labour, home maintenance) or add your own
- Each task has **adjustable mental-load points (1–10)** so heavier tasks weigh more
- Assign tasks to a partner, mark them **Shared**, or leave them **Unassigned**
- **Transfer tasks** between partners with a short message — the perfect lightweight way to ask for help
- **Couple chat & notes** for ongoing check-ins
- **Dashboard with clear visuals**: load-split donut, by-category stacked bars, fairness indicator, and a who-owns-what table
- **Save / load** household data as JSON so progress persists between sessions

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Then open the URL Streamlit prints (usually <http://localhost:8501>).

## Deploy on Streamlit Community Cloud
1. Push this repo to GitHub (already done if you're reading this on GitHub).
2. Go to <https://share.streamlit.io>, sign in with GitHub, and click **New app**.
3. Pick this repo, branch `main`, main file `app.py`.
4. Click **Deploy**. Done.

## Files
- `app.py` — the entire Streamlit app
- `requirements.txt` — Python dependencies
- `household_data.json` — auto-created when you click **Save** in the sidebar

## Roadmap ideas
- Per-partner login so each person sees a personalised view
- Weekly/monthly trend charts of the load split
- Reminders / nudges by email
- Mobile-friendly card layout for the task list
- Multi-household support
