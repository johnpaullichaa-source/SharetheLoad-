"""
Share the Load
A calm, minimal Streamlit app that helps couples see and rebalance
the mental load of running a household.

Design language
- Palette: sage + sand on warm off-white, single accent per chart
- Layout: hero "state of the household" on open, secondary detail behind tabs
- Tone: gentle, non-judgemental, suggests rather than alerts
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import storage


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Share the Load",
    page_icon="◐",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={"About": "Share the Load — a calm space to share the mental load."},
)

# iOS / mobile web-app meta tags so the page looks polished when added to Home Screen
st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="Share the Load">
    <meta name="theme-color" content="#F7F5F0">
    <link rel="apple-touch-icon" href="https://api.dicebear.com/7.x/shapes/svg?seed=sharetheload&backgroundColor=7BA098">
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
BG = "#F7F5F0"
SURFACE = "#FFFFFF"
BORDER = "#E8E4DC"
INK = "#2D3A36"
MUTED = "#7B8A85"
SAGE = "#7BA098"        # Partner A
SAND = "#C8A57A"        # Partner B
SHARED = "#A8B5A0"
SOFT = "#EFEBE3"
SUCCESS = "#6B8E7F"
WARN = "#C9A961"

CUSTOM_CSS = f"""
<style>
  /* Global */
  html, body, [class*="css"] {{
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
    color: {INK};
  }}
  .stApp {{
    background: {BG};
  }}
  /* Hide default menu and footer for a cleaner feel */
  #MainMenu, footer {{ visibility: hidden; }}
  /* Reduce top padding */
  .block-container {{ padding-top: 2.5rem; padding-bottom: 5rem; max-width: 760px; }}
  @media (max-width: 640px) {{
    .block-container {{ padding-top: 1.2rem; padding-left: 1rem; padding-right: 1rem; padding-bottom: env(safe-area-inset-bottom, 2rem); }}
    h1 {{ font-size: 1.4rem; }}
    .hero-headline {{ font-size: 1.3rem; }}
    .hero-sub {{ font-size: 0.95rem; }}
    .stat-num {{ font-size: 1.5rem; }}
  }}

  /* Bigger tap targets on touch devices */
  @media (pointer: coarse) {{
    .stButton>button, .stDownloadButton>button {{ min-height: 44px; padding: 0.7rem 1rem; }}
    .stTextInput input, .stNumberInput input {{ min-height: 44px; }}
    .stSelectbox div[data-baseweb] {{ min-height: 44px; }}
  }}

  /* Type */
  h1, h2, h3, h4 {{ color: {INK}; font-weight: 500; letter-spacing: -0.01em; }}
  h1 {{ font-size: 1.6rem; }}
  h2 {{ font-size: 1.25rem; }}
  h3 {{ font-size: 1.05rem; }}
  p, label, span, div {{ color: {INK}; }}
  .muted {{ color: {MUTED}; font-size: 0.92rem; }}
  .eyebrow {{
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-size: 0.72rem;
    color: {MUTED};
    margin-bottom: 0.3rem;
  }}
  .hero-headline {{
    font-size: 1.55rem;
    line-height: 1.35;
    font-weight: 500;
    color: {INK};
    margin: 0.3rem 0 0.6rem 0;
  }}
  .hero-sub {{
    color: {MUTED};
    font-size: 1rem;
    margin-bottom: 1.6rem;
  }}

  /* Card */
  .card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1rem;
  }}
  .card-quiet {{
    background: transparent;
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
  }}
  .stat-num {{ font-size: 1.9rem; font-weight: 500; color: {INK}; line-height: 1; }}
  .stat-label {{ font-size: 0.82rem; color: {MUTED}; margin-top: 0.3rem; }}

  /* Pills */
  .pill {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.74rem;
    background: {SOFT};
    color: {INK};
    margin-right: 6px;
  }}
  .pill-sage  {{ background: #E6EEEB; color: {SAGE}; }}
  .pill-sand  {{ background: #F1E8D9; color: #8E6E3F; }}
  .pill-shared {{ background: #ECEFE7; color: {SUCCESS}; }}

  /* Buttons */
  .stButton>button, .stDownloadButton>button {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    color: {INK};
    border-radius: 10px;
    padding: 0.45rem 1rem;
    font-weight: 500;
    transition: all 0.15s ease;
  }}
  .stButton>button:hover {{
    border-color: {SAGE};
    color: {SAGE};
  }}
  .stButton>button[kind="primary"] {{
    background: {INK};
    color: {BG};
    border: 1px solid {INK};
  }}
  .stButton>button[kind="primary"]:hover {{
    background: {SAGE};
    border-color: {SAGE};
    color: {SURFACE};
  }}

  /* Inputs */
  .stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox div[data-baseweb] {{
    background: {SURFACE} !important;
    border-radius: 10px !important;
  }}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{
    gap: 0.4rem;
    border-bottom: 1px solid {BORDER};
  }}
  .stTabs [data-baseweb="tab"] {{
    background: transparent;
    color: {MUTED};
    border-radius: 8px 8px 0 0;
    padding: 0.4rem 0.8rem;
    font-size: 0.92rem;
  }}
  .stTabs [aria-selected="true"] {{
    color: {INK};
    border-bottom: 2px solid {SAGE} !important;
  }}

  /* Dividers */
  hr {{ border-color: {BORDER}; }}

  /* Chat */
  [data-testid="stChatMessage"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
  }}

  /* Hide labels visually-only where we use label_visibility=collapsed */
  .row-task {{
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.5rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid {BORDER};
  }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
DEFAULT_TASKS = [
    # (name, category, points, frequency, invisible?)
    ("Plan weekly meals",                       "Food",        5, "Weekly",   True),
    ("Grocery shopping",                        "Food",        4, "Weekly",   False),
    ("Cooking dinner",                          "Food",        4, "Daily",    False),
    ("Packing lunches",                         "Food",        3, "Daily",    False),
    ("Dishes",                                  "Home",        2, "Daily",    False),
    ("Laundry",                                 "Home",        4, "Weekly",   False),
    ("Vacuuming & mopping",                     "Home",        3, "Weekly",   False),
    ("Cleaning bathrooms",                      "Home",        3, "Weekly",   False),
    ("Tidying common areas",                    "Home",        2, "Daily",    False),
    ("Taking out rubbish",                      "Home",        1, "Weekly",   False),
    ("School drop-off / pick-up",               "Kids",        4, "Daily",    False),
    ("Helping with homework",                   "Kids",        3, "Daily",    False),
    ("Bath & bedtime routine",                  "Kids",        4, "Daily",    False),
    ("Tracking school events",                  "Kids",        4, "Weekly",   True),
    ("Organising playdates / activities",       "Kids",        3, "Weekly",   True),
    ("Paying bills",                            "Admin",       4, "Monthly",  True),
    ("Budgeting & expense tracking",            "Admin",       5, "Monthly",  True),
    ("Booking appointments",                    "Admin",       4, "As needed", True),
    ("Car servicing / rego",                    "Admin",       3, "As needed", True),
    ("Buying gifts (family & friends)",         "Planning",    4, "Monthly",  True),
    ("Planning holidays",                       "Planning",    5, "As needed", True),
    ("Remembering birthdays",                   "Planning",    4, "Ongoing",  True),
    ("Family calendar",                         "Planning",    5, "Weekly",   True),
    ("Emotional check-ins",                     "Emotional",   5, "Daily",    True),
    ("Supporting kids' moods",                  "Emotional",   5, "As needed", True),
    ("Holding the mental to-do list",           "Emotional",   5, "Ongoing",  True),
    ("Garden / yard",                           "Home",        3, "Weekly",   False),
    ("Repairs & DIY",                           "Home",        3, "As needed", False),
    ("Pet care",                                "Home",        3, "Daily",    False),
]


def _empty_state() -> dict:
    return {
        "partner_a": "",
        "partner_b": "",
        "tasks": [],
        "messages": [],
        "transfers": [],
        "appreciations": [],
        "onboarded": False,
        "week_start": _week_start_iso(),
        "created_at": datetime.utcnow().isoformat(),
    }


def _week_start_iso() -> str:
    today = date.today()
    return (today - timedelta(days=today.weekday())).isoformat()


def _new_task(name, category, points, frequency, invisible=False, owner="Unassigned"):
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "category": category,
        "points": int(points),
        "frequency": frequency,
        "invisible": invisible,
        "owner": owner,
        "active_this_week": True,
    }


def seed_default_tasks():
    return [_new_task(*row) for row in DEFAULT_TASKS]


def get_household_id() -> str:
    # query param ?h=... lets a couple share one household by sharing the URL
    try:
        qp = st.query_params
        if "h" in qp and qp["h"]:
            val = qp["h"]
            return val if isinstance(val, str) else val[0]
    except Exception:
        pass
    return st.session_state.get("household_id", "default")


def load_state_from_disk() -> Optional[dict]:
    return storage.load(get_household_id())


def save_state_to_disk(state: dict) -> None:
    storage.save(state, get_household_id())


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "state" not in st.session_state:
    persisted = load_state_from_disk()
    if persisted:
        st.session_state.state = persisted
    else:
        s = _empty_state()
        s["tasks"] = seed_default_tasks()
        st.session_state.state = s

state = st.session_state.state
# Backfill any new fields on older saves
for key, default in _empty_state().items():
    state.setdefault(key, default)
for t in state["tasks"]:
    t.setdefault("invisible", False)
    t.setdefault("active_this_week", True)


def owner_options() -> list[str]:
    return [state["partner_a"] or "Partner 1", state["partner_b"] or "Partner 2", "Shared", "Unassigned"]


# ---------------------------------------------------------------------------
# Analytics helpers
# ---------------------------------------------------------------------------
def active_df() -> pd.DataFrame:
    rows = [t for t in state["tasks"] if t.get("active_this_week", True)]
    if not rows:
        return pd.DataFrame(columns=["id", "name", "category", "points", "frequency", "invisible", "owner", "active_this_week"])
    return pd.DataFrame(rows)


def _names() -> tuple[str, str]:
    a = (state.get("partner_a") or "").strip() or "Partner 1"
    b = (state.get("partner_b") or "").strip() or "Partner 2"
    if a == b:
        b = b + " (2)"
    return a, b


def split_points(df: pd.DataFrame) -> dict[str, float]:
    a, b = _names()
    totals: dict[str, float] = {a: 0.0, b: 0.0, "Unassigned": 0.0}
    if df is None or df.empty:
        return totals
    for _, r in df.iterrows():
        try:
            pts = float(r["points"])
        except (TypeError, ValueError):
            continue
        owner = r.get("owner", "Unassigned")
        if owner == a:
            totals[a] += pts
        elif owner == b:
            totals[b] += pts
        elif owner == "Shared":
            totals[a] += pts / 2
            totals[b] += pts / 2
        else:
            totals["Unassigned"] += pts
    return totals


def invisible_share(df: pd.DataFrame) -> dict[str, float]:
    a, b = _names()
    inv: dict[str, float] = {a: 0.0, b: 0.0}
    if df is None or df.empty:
        return inv
    for _, r in df.iterrows():
        if not r.get("invisible"):
            continue
        try:
            pts = float(r["points"])
        except (TypeError, ValueError):
            continue
        owner = r.get("owner", "Unassigned")
        if owner == a:
            inv[a] += pts
        elif owner == b:
            inv[b] += pts
        elif owner == "Shared":
            inv[a] += pts / 2
            inv[b] += pts / 2
    return inv


def biggest_transferable(df: pd.DataFrame, heavier: str) -> Optional[dict]:
    """Highest-points task owned solely by the heavier partner — best candidate to share."""
    if df is None or df.empty:
        return None
    candidates = df[df["owner"] == heavier].sort_values("points", ascending=False)
    if candidates.empty:
        return None
    row = candidates.iloc[0]
    return {
        "name": str(row.get("name", "")),
        "points": int(row.get("points", 0) or 0),
        "category": str(row.get("category", "")),
    }


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------
def render_onboarding():
    st.markdown('<div class="eyebrow">Welcome</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-headline">Let\'s set up your household.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">This takes about two minutes. Your data stays on this device — nothing is uploaded.</div>',
        unsafe_allow_html=True,
    )

    step = st.session_state.get("onboard_step", 1)

    if step == 1:
        with st.container():
            st.markdown("##### Your names")
            c1, c2 = st.columns(2)
            state["partner_a"] = c1.text_input("Partner 1", value=state["partner_a"], placeholder="e.g. Alex")
            state["partner_b"] = c2.text_input("Partner 2", value=state["partner_b"], placeholder="e.g. Sam")
            st.write("")
            if st.button("Continue", type="primary", use_container_width=True,
                         disabled=not (state["partner_a"].strip() and state["partner_b"].strip())):
                st.session_state.onboard_step = 2
                st.rerun()

    elif step == 2:
        a, b = state["partner_a"], state["partner_b"]
        st.markdown("##### Who currently does what?")
        st.markdown(
            f'<div class="muted">Tap through the list — pick {a}, {b}, Shared, or Skip. '
            "You can adjust everything later.</div>",
            unsafe_allow_html=True,
        )
        st.write("")

        idx = st.session_state.get("onboard_task_idx", 0)
        if idx >= len(state["tasks"]):
            st.session_state.onboard_step = 3
            st.rerun()

        t = state["tasks"][idx]
        st.markdown(
            f"<div class='card'>"
            f"<div class='muted'>Task {idx+1} of {len(state['tasks'])} · {t['category']}</div>"
            f"<div style='font-size:1.2rem; margin:0.4rem 0 0.2rem 0;'>{t['name']}</div>"
            f"<div class='muted'>{t['frequency']} · weight {t['points']}"
            + (" · invisible work" if t['invisible'] else "")
            + "</div></div>",
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns(4)
        if c1.button(a, use_container_width=True, key=f"ob_a_{idx}"):
            t["owner"] = a; _advance()
        if c2.button(b, use_container_width=True, key=f"ob_b_{idx}"):
            t["owner"] = b; _advance()
        if c3.button("Shared", use_container_width=True, key=f"ob_s_{idx}"):
            t["owner"] = "Shared"; _advance()
        if c4.button("Skip", use_container_width=True, key=f"ob_sk_{idx}"):
            t["active_this_week"] = False
            t["owner"] = "Unassigned"; _advance()

        st.write("")
        st.markdown(f"<div class='muted' style='text-align:center'>Progress: {idx}/{len(state['tasks'])}</div>", unsafe_allow_html=True)
        if st.button("Finish setup now", use_container_width=True):
            st.session_state.onboard_step = 3
            st.rerun()

    elif step == 3:
        st.markdown('<div class="hero-headline">You\'re all set.</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hero-sub">Open the dashboard to see the state of your household.</div>',
            unsafe_allow_html=True,
        )
        if st.button("See our household", type="primary", use_container_width=True):
            state["onboarded"] = True
            save_state_to_disk(state)
            st.rerun()


def _advance():
    st.session_state.onboard_task_idx = st.session_state.get("onboard_task_idx", 0) + 1
    st.rerun()


# ---------------------------------------------------------------------------
# Hero / State of the household
# ---------------------------------------------------------------------------
def render_hero():
    a, b = _names()

    df = active_df()
    totals = split_points(df)
    assigned = totals[a] + totals[b]
    unassigned = totals["Unassigned"]

    # Eyebrow — tolerate missing/old week_start
    try:
        week_label = datetime.fromisoformat(state.get("week_start") or _week_start_iso()).strftime("Week of %d %B")
    except Exception:
        week_label = "This week"
    st.markdown(f'<div class="eyebrow">◐  Share the Load · {week_label}</div>', unsafe_allow_html=True)

    # Headline
    if assigned == 0:
        headline = f"Hi {a} and {b} — let's see your household."
        sub = "Assign a few tasks to start seeing your balance."
    else:
        share_a = totals[a] / assigned * 100
        share_b = totals[b] / assigned * 100
        gap = abs(share_a - share_b)
        heavier = a if totals[a] > totals[b] else b
        if gap <= 10:
            headline = "Your household feels balanced."
            sub = f"You're sharing the load almost evenly this week. Nicely done."
        elif gap <= 25:
            headline = f"Things are leaning toward {heavier}."
            sub = f"A small rebalance could even things out — there's a suggestion below."
        else:
            headline = f"{heavier} is carrying more this week."
            sub = "Worth a short conversation. A starting point is suggested below."

    st.markdown(f'<div class="hero-headline">{headline}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">{sub}</div>', unsafe_allow_html=True)

    # Balance visual — single donut, calm palette
    if assigned > 0:
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=[a, b],
                    values=[totals[a], totals[b]],
                    hole=0.72,
                    marker=dict(colors=[SAGE, SAND], line=dict(color=BG, width=4)),
                    textinfo="none",
                    hoverinfo="label+percent",
                    sort=False,
                )
            ]
        )
        share_a_pct = totals[a] / assigned * 100
        fig.update_layout(
            showlegend=False,
            height=260,
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor=BG,
            annotations=[
                dict(
                    text=f"<span style='font-size:28px;color:{INK}'>{share_a_pct:.0f} / {100-share_a_pct:.0f}</span><br>"
                         f"<span style='font-size:11px;color:{MUTED};letter-spacing:1px'>BALANCE</span>",
                    x=0.5, y=0.5, showarrow=False,
                )
            ],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Partner labels under donut
        c1, c2 = st.columns(2)
        c1.markdown(
            f"<div style='text-align:center'>"
            f"<span style='display:inline-block;width:10px;height:10px;background:{SAGE};border-radius:2px;margin-right:8px;vertical-align:middle'></span>"
            f"<span style='color:{INK}'>{a}</span><br>"
            f"<span class='muted'>{totals[a]:.0f} pts</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        c2.markdown(
            f"<div style='text-align:center'>"
            f"<span style='display:inline-block;width:10px;height:10px;background:{SAND};border-radius:2px;margin-right:8px;vertical-align:middle'></span>"
            f"<span style='color:{INK}'>{b}</span><br>"
            f"<span class='muted'>{totals[b]:.0f} pts</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    # Three quiet stats
    inv = invisible_share(df)
    inv_total = inv[a] + inv[b]
    inv_pct = (inv_total / assigned * 100) if assigned else 0

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            f"<div class='card-quiet'><div class='stat-num'>{int(assigned)}</div>"
            f"<div class='stat-label'>Total load points this week</div></div>",
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f"<div class='card-quiet'><div class='stat-num'>{inv_pct:.0f}%</div>"
            f"<div class='stat-label'>Is invisible work</div></div>",
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            f"<div class='card-quiet'><div class='stat-num'>{int(unassigned)}</div>"
            f"<div class='stat-label'>Unassigned points</div></div>",
            unsafe_allow_html=True,
        )

    # Suggested next step — only when meaningful
    if assigned > 0:
        share_a = totals[a] / assigned * 100
        share_b = totals[b] / assigned * 100
        gap = abs(share_a - share_b)
        if gap > 15:
            heavier = a if totals[a] > totals[b] else b
            lighter = b if heavier == a else a
            candidate = biggest_transferable(df, heavier)
            if candidate is not None:
                st.markdown(
                    f"<div class='card'>"
                    f"<div class='eyebrow'>A small suggestion</div>"
                    f"<div style='font-size:1.05rem;margin-bottom:0.4rem'>"
                    f"Consider sharing <b>{candidate['name']}</b> with {lighter}.</div>"
                    f"<div class='muted'>It's currently the heaviest task on {heavier}'s plate "
                    f"({int(candidate['points'])} pts). Even moving it to Shared would noticeably ease the balance.</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # Recent appreciation (one) — tolerate older entries missing fields
    if state.get("appreciations"):
        latest = state["appreciations"][-1] or {}
        text = str(latest.get("text", "")).strip()
        if text:
            frm = str(latest.get("from", ""))
            to = str(latest.get("to", ""))
            st.markdown(
                f"<div class='card-quiet'>"
                f"<div class='eyebrow'>A recent thank-you</div>"
                f"<div style='font-size:1rem;margin-top:0.3rem'>"
                f"<i>&ldquo;{text}&rdquo;</i></div>"
                f"<div class='muted' style='margin-top:0.3rem'>{frm} → {to}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Tasks view
# ---------------------------------------------------------------------------
def _snapshot_tasks() -> str:
    """Lightweight signature of current task state so we can detect unsaved edits."""
    return json.dumps(
        [
            (t["id"], t["name"], t["category"], t["points"], t["frequency"],
             t["invisible"], t["owner"], t.get("active_this_week", True))
            for t in state["tasks"]
        ],
        sort_keys=True,
    )


def render_tasks():
    a = state["partner_a"] or "Partner 1"
    b = state["partner_b"] or "Partner 2"

    st.markdown('<div class="eyebrow">Tasks</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-headline">What you do, together.</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-sub">Mark who currently does each one. Adjust the weight if a task feels heavier or lighter than the default. Tap Save changes at the bottom when you\'re done.</div>',
        unsafe_allow_html=True,
    )

    # Track the last-saved task signature in session state so we can show
    # whether there are unsaved edits.
    if "saved_snapshot" not in st.session_state:
        st.session_state.saved_snapshot = _snapshot_tasks()

    df = active_df()
    if len(state["tasks"]):
        cats = sorted({t["category"] for t in state["tasks"]})
        c1, c2 = st.columns([2, 3])
        cat_filter = c1.selectbox("Category", ["All"] + cats, label_visibility="collapsed")
        search = c2.text_input("Search", placeholder="Search tasks…", label_visibility="collapsed")
    else:
        cat_filter, search = "All", ""

    # Add task
    with st.expander("Add a task"):
        with st.form("add", clear_on_submit=True):
            c1, c2 = st.columns([3, 2])
            new_name = c1.text_input("Name")
            new_cat = c2.text_input("Category", value="Custom")
            c3, c4, c5 = st.columns(3)
            new_pts = c3.number_input("Weight", 1, 10, 3)
            new_freq = c4.selectbox("Frequency", ["Daily", "Weekly", "Monthly", "As needed", "Ongoing"])
            new_owner = c5.selectbox("Owner", owner_options())
            new_inv = st.checkbox("This is invisible mental work")
            if st.form_submit_button("Add", type="primary"):
                if new_name.strip():
                    state["tasks"].append(_new_task(new_name.strip(), new_cat, new_pts, new_freq, new_inv, new_owner))
                    save_state_to_disk(state)
                    st.session_state.saved_snapshot = _snapshot_tasks()
                    st.rerun()

    st.write("")

    # List
    for t in state["tasks"]:
        if cat_filter != "All" and t["category"] != cat_filter:
            continue
        if search and search.lower() not in t["name"].lower():
            continue

        with st.container():
            top = st.columns([6, 2])
            with top[0]:
                inv_tag = "<span class='pill'>invisible</span>" if t["invisible"] else ""
                active_tag = "" if t.get("active_this_week", True) else "<span class='pill' style='background:#F1ECE2;color:#9A8862'>paused this week</span>"
                st.markdown(
                    f"<div style='padding-top:0.4rem'>"
                    f"<div style='font-size:1.02rem;color:{INK}'>{t['name']}</div>"
                    f"<div class='muted' style='margin-top:2px'>{t['category']} · {t['frequency']} {inv_tag} {active_tag}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with top[1]:
                opts = owner_options()
                idx = opts.index(t["owner"]) if t["owner"] in opts else len(opts) - 1
                t["owner"] = st.selectbox(
                    "Owner", opts, index=idx, key=f"own_{t['id']}", label_visibility="collapsed",
                )

            bot = st.columns([2, 2, 2, 2])
            t["points"] = bot[0].number_input(
                "Weight", 1, 10, int(t["points"]),
                key=f"pts_{t['id']}", label_visibility="collapsed",
            )
            t["invisible"] = bot[1].checkbox("Invisible", value=t["invisible"], key=f"inv_{t['id']}")
            t["active_this_week"] = bot[2].checkbox("This week", value=t.get("active_this_week", True), key=f"act_{t['id']}")
            if bot[3].button("Remove", key=f"del_{t['id']}"):
                state["tasks"] = [x for x in state["tasks"] if x["id"] != t["id"]]
                save_state_to_disk(state)
                st.session_state.saved_snapshot = _snapshot_tasks()
                st.rerun()

            st.markdown("<hr style='margin:0.4rem 0 0 0;border:none;border-top:1px solid " + BORDER + "'>", unsafe_allow_html=True)

    # ---- Sticky save bar ----
    has_changes = _snapshot_tasks() != st.session_state.saved_snapshot
    st.write("")
    st.markdown(
        f"<div style='position:sticky;bottom:0;background:{BG};padding:0.8rem 0 0.4rem 0;"
        f"border-top:1px solid {BORDER};margin-top:1.2rem;z-index:5;'></div>",
        unsafe_allow_html=True,
    )
    sc1, sc2 = st.columns([3, 2])
    with sc1:
        if has_changes:
            st.markdown(
                f"<div class='muted' style='padding-top:0.5rem'>You have unsaved changes.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='muted' style='padding-top:0.5rem'>All changes saved.</div>",
                unsafe_allow_html=True,
            )
    with sc2:
        if st.button(
            "Save changes" if has_changes else "Saved",
            type="primary",
            use_container_width=True,
            disabled=not has_changes,
            key="save_tasks_btn",
        ):
            save_state_to_disk(state)
            st.session_state.saved_snapshot = _snapshot_tasks()
            st.toast("Saved — your household is up to date.", icon="✓")
            st.rerun()


# ---------------------------------------------------------------------------
# Transfer
# ---------------------------------------------------------------------------
def render_transfer():
    st.markdown('<div class="eyebrow">Transfer</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-headline">Hand a task over.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">Pick a task, choose who takes it next, and leave a short note so it doesn\'t feel out of nowhere.</div>',
        unsafe_allow_html=True,
    )

    df = active_df()
    if df.empty:
        st.info("No tasks yet.")
        return

    with st.form("transfer", clear_on_submit=True):
        task_map = {f"{t['name']}  ·  with {t['owner']}": t["id"] for t in state["tasks"]}
        chosen = st.selectbox("Task", list(task_map.keys()))
        new_owner = st.selectbox("Hand to", owner_options())
        msg = st.text_area("Note", placeholder="e.g. Could you take this for the next two weeks? Work is heavy right now.")
        if st.form_submit_button("Transfer", type="primary"):
            tid = task_map[chosen]
            old = None
            for t in state["tasks"]:
                if t["id"] == tid:
                    old = t["owner"]
                    t["owner"] = new_owner
            state["transfers"].append({
                "task": chosen.split("  ·  ")[0],
                "from": old, "to": new_owner, "message": msg,
                "at": datetime.utcnow().isoformat(),
            })
            if msg.strip():
                state["messages"].append({
                    "author": old or "System",
                    "text": f"Transferred '{chosen.split('  ·  ')[0]}' to {new_owner} — {msg}",
                    "at": datetime.utcnow().isoformat(),
                })
            save_state_to_disk(state)
            st.success("Transferred.")

    if state["transfers"]:
        st.markdown('<div class="eyebrow" style="margin-top:1.5rem">Recent transfers</div>', unsafe_allow_html=True)
        for tr in reversed(state["transfers"][-8:]):
            ts = datetime.fromisoformat(tr["at"]).strftime("%d %b · %H:%M")
            note = f"<div class='muted' style='margin-top:4px'><i>{tr['message']}</i></div>" if tr["message"] else ""
            st.markdown(
                f"<div class='card-quiet'>"
                f"<div style='color:{INK}'>{tr['task']}</div>"
                f"<div class='muted' style='margin-top:2px'>{tr['from']} → {tr['to']} · {ts}</div>"
                f"{note}</div>",
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Chat & Appreciation
# ---------------------------------------------------------------------------
def render_chat():
    a = state["partner_a"] or "Partner 1"
    b = state["partner_b"] or "Partner 2"

    st.markdown('<div class="eyebrow">Talk</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-headline">A quiet space for the two of you.</div>', unsafe_allow_html=True)

    sub_appr, sub_chat = st.tabs(["Appreciation", "Notes"])

    with sub_appr:
        st.markdown(
            f"<div class='muted' style='margin-bottom:0.8rem'>"
            f"One of the strongest signals of a healthy partnership is regular thanks. "
            f"Drop a quick note for something specific.</div>",
            unsafe_allow_html=True,
        )
        with st.form("appr", clear_on_submit=True):
            c1, c2 = st.columns(2)
            frm = c1.selectbox("From", [a, b])
            to = c2.selectbox("To", [b, a])
            text = st.text_area("What for?", placeholder="e.g. Thanks for handling bedtime three nights in a row this week.")
            if st.form_submit_button("Send appreciation", type="primary"):
                if text.strip():
                    state["appreciations"].append({
                        "from": frm, "to": to, "text": text.strip(),
                        "at": datetime.utcnow().isoformat(),
                    })
                    save_state_to_disk(state)
                    st.rerun()

        if state["appreciations"]:
            st.write("")
            for x in reversed(state["appreciations"][-10:]):
                ts = datetime.fromisoformat(x["at"]).strftime("%d %b")
                st.markdown(
                    f"<div class='card-quiet'>"
                    f"<i style='color:{INK}'>&ldquo;{x['text']}&rdquo;</i>"
                    f"<div class='muted' style='margin-top:0.4rem'>{x['from']} → {x['to']} · {ts}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    with sub_chat:
        with st.form("msg", clear_on_submit=True):
            author = st.selectbox("From", [a, b], key="msg_author")
            text = st.text_area("Message", placeholder="Anything you want to flag, plan, or check in about.")
            if st.form_submit_button("Send", type="primary"):
                if text.strip():
                    state["messages"].append({
                        "author": author, "text": text.strip(),
                        "at": datetime.utcnow().isoformat(),
                    })
                    save_state_to_disk(state)
                    st.rerun()

        for m in reversed(state["messages"][-30:]):
            ts = datetime.fromisoformat(m["at"]).strftime("%d %b · %H:%M")
            with st.chat_message("user" if m["author"] == a else "assistant"):
                st.markdown(f"**{m['author']}**  ·  <span class='muted'>{ts}</span>", unsafe_allow_html=True)
                st.write(m["text"])


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
def render_settings():
    st.markdown('<div class="eyebrow">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-headline">Your household.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">Names, week, and data. Everything stays on your device.</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    state["partner_a"] = c1.text_input("Partner 1", value=state["partner_a"])
    state["partner_b"] = c2.text_input("Partner 2", value=state["partner_b"])

    st.write("")
    st.markdown("##### Weekly rhythm")
    st.markdown(
        f"<div class='muted'>Current week starts <b>"
        f"{datetime.fromisoformat(state['week_start']).strftime('%d %B %Y')}</b>. "
        "Start a fresh week to mark everything active again.</div>",
        unsafe_allow_html=True,
    )
    if st.button("Start a fresh week"):
        state["week_start"] = _week_start_iso()
        for t in state["tasks"]:
            t["active_this_week"] = True
        save_state_to_disk(state)
        st.success("New week started.")

    st.write("")
    st.markdown("##### Sync")
    if storage.using_cloud():
        st.markdown(
            f"<div class='muted'>✓ Connected to your shared household. "
            f"Both phones using the same link will see the same data.</div>",
            unsafe_allow_html=True,
        )
        current_hh = get_household_id()
        new_hh = st.text_input("Household ID", value=current_hh, help="Anyone with the same Household ID sees the same data.")
        if new_hh != current_hh:
            st.session_state.household_id = new_hh
            try:
                st.query_params["h"] = new_hh
            except Exception:
                pass
            st.rerun()
    else:
        st.markdown(
            "<div class='muted'>Currently saving to this device only. "
            "Add Supabase keys in your Streamlit secrets to sync between phones — see the README.</div>",
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown("##### Data")
    c1, c2 = st.columns(2)
    if c1.button("Save now", use_container_width=True):
        save_state_to_disk(state)
        st.success("Saved.")
    c2.download_button(
        "Download data",
        data=json.dumps(state, indent=2),
        file_name="sharetheload.json",
        mime="application/json",
        use_container_width=True,
    )
    up = st.file_uploader("Restore from file", type=["json"])
    if up is not None:
        try:
            st.session_state.state = json.loads(up.read().decode("utf-8"))
            st.success("Restored — refreshing…")
            st.rerun()
        except Exception as e:
            st.error(str(e))

    st.write("")
    st.markdown("##### Start over")
    if st.button("Reset to defaults"):
        s = _empty_state()
        s["tasks"] = seed_default_tasks()
        st.session_state.state = s
        save_state_to_disk(s)
        st.session_state.onboard_step = 1
        st.session_state.onboard_task_idx = 0
        st.rerun()


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
if not state.get("onboarded"):
    render_onboarding()
else:
    # Top-level minimal nav
    tabs = st.tabs(["Home", "Tasks", "Transfer", "Talk", "Settings"])

    def _safe(render_fn, label):
        try:
            render_fn()
        except Exception as e:
            st.markdown(
                f"<div class='card-quiet' style='border-color:#E2D5C3'>"
                f"<div class='eyebrow'>Hmm</div>"
                f"<div style='margin-top:0.3rem'>Something didn't render quite right on the {label} screen.</div>"
                f"<div class='muted' style='margin-top:0.3rem'>Try refreshing the page — your data is safe.</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            with st.expander("Technical details"):
                st.exception(e)

    with tabs[0]:
        _safe(render_hero, "Home")
    with tabs[1]:
        render_tasks()
    with tabs[2]:
        _safe(render_transfer, "Transfer")
    with tabs[3]:
        _safe(render_chat, "Talk")
    with tabs[4]:
        _safe(render_settings, "Settings")
