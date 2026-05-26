# Get Share the Load onto your iPhones

This guide takes about **15 minutes total**. You'll end up with an icon on both
of your home screens that opens fullscreen, looks like an app, and syncs data
between the two of you.

There are three short steps:

1. **Deploy** the app online (free)
2. **Sync** — connect a free Supabase database so both phones share the same data
3. **Install** — add the app to each iPhone's home screen

---

## 1. Deploy on Streamlit Community Cloud (5 minutes)

1. Go to <https://share.streamlit.io> and sign in with your GitHub account.
2. Click **New app** (or **Create app**).
3. Pick:
   - Repository: `johnpaullichaa-source/SharetheLoad-`
   - Branch: `main`
   - Main file path: `app.py`
4. Click **Deploy**.

In about a minute you'll get a public URL like
`https://sharetheload-xxxxx.streamlit.app`. Open it — the app is live.

At this point the app works but saves data **per-device** (so your phone and your
wife's phone would each have their own copy). Step 2 fixes that.

---

## 2. Add cloud sync with Supabase (8 minutes)

Supabase gives you a free Postgres database. We'll use one tiny table.

### 2a. Create the database

1. Go to <https://supabase.com> → **Start your project** → sign in with GitHub.
2. Click **New project**.
   - Name: `sharetheload` (anything works)
   - Database password: pick anything, you won't need it again
   - Region: closest to you (Sydney for Australia)
3. Wait ~1 min for it to provision.
4. Once ready, click **SQL Editor** in the left sidebar → **New query**, paste this and click **Run**:

   ```sql
   create table if not exists households (
       id text primary key,
       data jsonb not null,
       updated_at timestamp with time zone default now()
   );

   alter table households enable row level security;

   create policy "allow anon read"
       on households for select
       to anon using (true);

   create policy "allow anon write"
       on households for insert
       to anon with check (true);

   create policy "allow anon update"
       on households for update
       to anon using (true) with check (true);
   ```

5. Click **Project Settings** (gear icon) → **API**. Copy two values:
   - **Project URL** (looks like `https://abcd1234.supabase.co`)
   - **anon public** key (long string starting with `eyJ...`)

### 2b. Tell Streamlit about them

1. Go back to your app on <https://share.streamlit.io>.
2. Click the **⋮** menu next to your app → **Settings** → **Secrets**.
3. Paste this, replacing with your values:

   ```toml
   SUPABASE_URL = "https://abcd1234.supabase.co"
   SUPABASE_ANON_KEY = "eyJhbGciOi...rest-of-anon-key"
   ```

4. Click **Save**. The app will reboot in ~30 seconds.

### 2c. Pick a household ID

When you open the app now, go to **Settings → Sync**. It should say
"✓ Connected to your shared household".

Change the **Household ID** to something only you two would use, e.g.
`lichaa-household-7491`. The app's URL becomes
`https://sharetheload-xxxxx.streamlit.app/?h=lichaa-household-7491`.

**This is the URL you both bookmark.** Anyone with that exact URL sees the same
data — anyone without it doesn't. (The ID acts as a shared key. Pick something
unguessable.)

---

## 3. Add to iPhone Home Screen (1 minute per phone)

On **each** iPhone:

1. Open the household URL in **Safari** (must be Safari, not Chrome).
2. Tap the **Share** button (square with up arrow) at the bottom.
3. Scroll down and tap **Add to Home Screen**.
4. Name it **Share the Load** → tap **Add**.

The icon appears on your home screen. Tapping it opens the app **fullscreen**
with no Safari bar — it looks and feels like a native iOS app.

---

## Bookmark this

After deploy, the URL you and your wife use forever is:

```
https://YOUR-APP-NAME.streamlit.app/?h=YOUR-HOUSEHOLD-ID
```

Save it. Share it between phones via iMessage or AirDrop, then both of you do
the Add-to-Home-Screen step.

---

## Troubleshooting

- **"Currently saving to this device only" in Settings** — Secrets aren't set
  correctly. Double-check you copied the **anon public** key, not the service
  role key, and that the variable names match exactly (`SUPABASE_URL`,
  `SUPABASE_ANON_KEY`).
- **App reboots after editing secrets and then errors** — give it 30 seconds.
  If still erroring, check the logs at the bottom of the Streamlit app page.
- **One phone shows different data than the other** — confirm the URL is
  identical on both phones, including the `?h=...` part.
- **Want to start fresh** — go to Settings → "Reset to defaults". This clears
  the current household ID's data in Supabase.

---

## What this costs

- Streamlit Community Cloud: **free**
- Supabase free tier: **free** (500 MB database, way more than you'll use)
- Total: **$0/month**
