# Get Share the Load onto your iPhones

Your Supabase database is already set up. You only need to do **two short steps**:

1. **Deploy** the Streamlit app (5 minutes)
2. **Add to Home Screen** on each iPhone (1 minute per phone)

The Supabase URL and anon key for your project are provided separately by your assistant — paste them into Streamlit in Step 1 below. The `households` table and security policies are already in place.

---

## Step 1 — Deploy on Streamlit Community Cloud (5 minutes)

1. Go to <https://share.streamlit.io> and sign in with your GitHub account.
2. Click **Create app** → **Deploy a public app from GitHub**.
3. Fill in:
   - Repository: `johnpaullichaa-source/SharetheLoad-`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: pick something memorable, e.g. `sharetheload-lichaa`
4. Before clicking Deploy, click **Advanced settings** → **Secrets**, and paste:

   ```toml
   SUPABASE_URL = "<your supabase url>"
   SUPABASE_ANON_KEY = "<your supabase anon key>"
   ```

5. Click **Deploy**.

After about a minute the app is live at your chosen URL.

### Pick a household ID

Open the app, complete the short onboarding, then go to **Settings → Sync**.
You should see "✓ Connected to your shared household".

Change the Household ID to something only you two would use, e.g.
`lichaa-household-7491`. The URL you and your wife will bookmark is:

```
https://YOUR-APP-NAME.streamlit.app/?h=lichaa-household-7491
```

Anyone with that exact URL sees the same data; anyone without it doesn't.

---

## Step 2 — Add to iPhone Home Screen (1 minute per phone)

On **each** iPhone, in **Safari** (not Chrome):

1. Open `https://YOUR-APP-NAME.streamlit.app/?h=lichaa-household-7491`
2. Tap the **Share** button (square with up arrow).
3. Scroll down and tap **Add to Home Screen**.
4. Name it **Share the Load** → tap **Add**.

The icon now lives on your home screen. Tapping it opens the app fullscreen —
no Safari bar, looks and feels like a native iOS app.

---

## Troubleshooting

- **"Currently saving to this device only" in Settings** — Secrets aren't loaded.
  Double-check you pasted them in **Streamlit's** Secrets panel (not Supabase),
  and that the variable names match exactly: `SUPABASE_URL`, `SUPABASE_ANON_KEY`.
- **One phone shows different data than the other** — confirm the URL is
  identical on both phones, including the `?h=...` part.
- **Want to wipe everything and start fresh** — Settings → "Reset to defaults".

---

## What this costs

- Streamlit Community Cloud: **free**
- Supabase (your `sharetheload` project): **free**
- Total: **$0/month**
