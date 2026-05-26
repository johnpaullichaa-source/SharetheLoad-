"""
Share the Load
A Streamlit app to help couples share the mental load of running a household.

Features
- Onboard both partners with their names and a shared household
- Curated, editable task library (cooking, cleaning, kids, admin, planning, emotional labour)
- Per-task mental-load points (adjustable) so heavier tasks weigh more
- Assign tasks to a partner or mark as "Shared"
- Transfer tasks between partners with a short note (mini communication log)
- Couple chat / notes section for ongoing communication
- Dashboard with clear visuals: load split, category breakdown, who owns what
- Suggestions for rebalancing when the split is uneven
- Save / load household data as JSON so progress persists between sessions
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ---------------------------------------------------------------------------
# Page config and styling
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Share the Load",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #2E4057;
        margin-bottom: 0.2rem;
    }
    .tagline {
        color: #6c7a89;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%);
        border: 1px solid #e6ecf2;
        border-radius: 12px;
        padding: 1rem 1.25rem;
    }
    .pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        margin-right: 4px;
        background: #eef3f8;
        color: #2E4057;
    }
    .stButton>button {
        border-radius: 8px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
DATA_FILE = Path("household_data.json")

DEFAULT_TASKS = [
    # (name, category, points, default frequency text)
    ("Plan weekly meals", "Cooking & Food", 5, "Weekly"),
    ("Grocery shopping", "Cooking & Food", 4, "Weekly"),
    ("Cooking dinner", "Cooking & Food", 4, "Daily"),
    ("Packing school/work lunches", "Cooking & Food", 3, "Daily"),
    ("Doing the dishes", "Cleaning", 2, "Daily"),
    ("Laundry (wash/dry/fold)", "Cleaning", 4, "Weekly"),
    ("Vacuuming & mopping", "Cleaning", 3, "Weekly"),
    ("Cleaning bathrooms", "Cleaning", 3, "Weekly"),
    ("Tidying common areas", "Cleaning", 2, "Daily"),
    ("Taking out rubbish/recycling", "Cleaning", 1, "Weekly"),
    ("School drop-off / pick-up", "Kids", 4, "Daily"),
    ("Helping with homework", "Kids", 3, "Daily"),
    ("Bath & bedtime routine", "Kids", 4, "Daily"),
    ("Organising playdates / activities", "Kids", 3, "Weekly"),
    ("Tracking school events & permission slips", "Kids", 4, "Weekly"),
    ("Paying bills", "Admin & Finance", 4, "Monthly"),
    ("Budgeting & expense tracking", "Admin & Finance", 5, "Monthly"),
    ("Booking medical / dental appointments", "Admin & Finance", 4, "As needed"),
    ("Car servicing / rego / insurance", "Admin & Finance", 3, "As needed"),
    ("Buying birthday gifts (family & friends)", "Planning & Social", 4, "Monthly"),
    ("Planning holidays / trips", "Planning & Social", 5, "As needed"),
    ("Remembering birthdays & anniversaries", "Planning & Social", 4, "Ongoing"),
    ("Organising family calendar", "Planning & Social", 5, "Weekly"),
    ("Checking in emotionally with partner", "Emotional Labour", 5, "Daily"),
    ("Mediating arguments / supporting kids", "Emotional Labour", 5, "As needed"),
    ("Staying on top of household to-dos", "Emotional Labour", 5, "Ongoing"),
    ("Garden / yard maintenance", "Home Maintenance", 3, "Weekly"),
    ("Minor repairs & DIY", "Home Maintenance", 3, "As needed"),
    ("Pet care (food/vet/walks)", "Home Maintenance", 3, "Daily"),
]


def _empty_state() -> dict:
    return {
        "partner_a": "Partner A",
        "partner_b": "Partner B",
        "tasks": [],  # list of task dicts
        "messages": [],  # chat / note log
        "transfers": [],  # transfer history
        "created_at": datetime.utcnow().isoformat(),
    }


def _new_task(name: str, category: str, points: int, frequency: str, owner: str = "Unassigned") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "category": category,
        "points": int(points),
        "frequency": frequency,
        "owner": owner,  # one of partner_a name, partner_b name, "Shared", "Unassigned"
        "notes": "",
        "created_at": datetime.utcnow().isoformat(),
    }


def seed_default_tasks() -> list[dict]:
    return [_new_task(n, c, p, f) for n, c, p, f in DEFAULT_TASKS]


def load_state_from_disk() -> Optional[dict]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            return None
    return None


def save_state_to_disk(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "state" not in st.session_state:
    persisted = load_state_from_disk()
    if persisted:
        st.session_state.state = persisted
    else:
        st.session_state.state = _empty_state()
        st.session_state.state["tasks"] = seed_default_tasks()

state = st.session_state.state


def owner_options() -> list[str]:
    return [state["partner_a"], state["partner_b"], "Shared", "Unassigned"]


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<div class="main-title">🤝 Share the Load</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="tagline">A friendlier way for couples to see, share, and rebalance the mental load of running a household.</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Sidebar: couple setup & data controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("👥 Your household")
    state["partner_a"] = st.text_input("Partner 1 name", value=state["partner_a"])
    state["partner_b"] = st.text_input("Partner 2 name", value=state["partner_b"])

    st.divider()
    st.subheader("💾 Data")
    col_s, col_l = st.columns(2)
    with col_s:
        if st.button("Save", use_container_width=True):
            save_state_to_disk(state)
            st.success("Saved")
    with col_l:
        if st.button("Reload", use_container_width=True):
            persisted = load_state_from_disk()
            if persisted:
                st.session_state.state = persisted
                st.rerun()
            else:
                st.info("Nothing saved yet")

    st.download_button(
        "⬇️ Download data (JSON)",
        data=json.dumps(state, indent=2),
        file_name="sharetheload_data.json",
        mime="application/json",
        use_container_width=True,
    )
    uploaded = st.file_uploader("⬆️ Upload data (JSON)", type=["json"])
    if uploaded is not None:
        try:
            st.session_state.state = json.loads(uploaded.read().decode("utf-8"))
            st.success("Imported — refresh to view")
            st.rerun()
        except Exception as e:
            st.error(f"Could not import: {e}")

    st.divider()
    if st.button("♻️ Reset everything", use_container_width=True):
        st.session_state.state = _empty_state()
        st.session_state.state["tasks"] = seed_default_tasks()
        st.rerun()


# ---------------------------------------------------------------------------
# Helpers for analytics
# ---------------------------------------------------------------------------
def tasks_df() -> pd.DataFrame:
    if not state["tasks"]:
        return pd.DataFrame(columns=["id", "name", "category", "points", "frequency", "owner", "notes"])
    return pd.DataFrame(state["tasks"])


def points_by_owner(df: pd.DataFrame) -> dict[str, float]:
    """Split points; shared tasks count half to each partner."""
    a, b = state["partner_a"], state["partner_b"]
    totals = {a: 0.0, b: 0.0, "Unassigned": 0.0}
    for _, row in df.iterrows():
        pts = float(row["points"])
        if row["owner"] == a:
            totals[a] += pts
        elif row["owner"] == b:
            totals[b] += pts
        elif row["owner"] == "Shared":
            totals[a] += pts / 2
            totals[b] += pts / 2
        else:
            totals["Unassigned"] += pts
    return totals


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_dashboard, tab_tasks, tab_transfer, tab_chat, tab_tips = st.tabs(
    ["📊 Dashboard", "📝 Tasks", "🔄 Transfer", "💬 Chat & Notes", "💡 Tips"]
)


# ---------------------------------------------------------------------------
# Dashboard tab
# ---------------------------------------------------------------------------
with tab_dashboard:
    df = tasks_df()
    a, b = state["partner_a"], state["partner_b"]

    if df.empty:
        st.info("No tasks yet — head over to the Tasks tab to add some.")
    else:
        totals = points_by_owner(df)
        total_load = sum(totals.values()) or 1.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total tasks", len(df))
        c2.metric(f"{a}'s load", f"{totals[a]:.1f} pts", f"{totals[a]/total_load*100:.0f}%")
        c3.metric(f"{b}'s load", f"{totals[b]:.1f} pts", f"{totals[b]/total_load*100:.0f}%")
        c4.metric("Unassigned", f"{totals['Unassigned']:.1f} pts")

        st.divider()

        left, right = st.columns([1, 1])

        # Split donut
        with left:
            st.subheader("Mental load split")
            assigned_total = totals[a] + totals[b]
            if assigned_total == 0:
                st.info("Assign some tasks to see the split.")
            else:
                pie_df = pd.DataFrame(
                    {"Partner": [a, b], "Points": [totals[a], totals[b]]}
                )
                fig = px.pie(
                    pie_df,
                    names="Partner",
                    values="Points",
                    hole=0.55,
                    color="Partner",
                    color_discrete_map={a: "#4C9AFF", b: "#FF8B94"},
                )
                fig.update_traces(textinfo="percent+label")
                fig.update_layout(showlegend=True, height=380, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig, use_container_width=True)

                # Balance bar / fairness indicator
                share_a = totals[a] / assigned_total * 100
                share_b = totals[b] / assigned_total * 100
                gap = abs(share_a - share_b)
                if gap <= 10:
                    st.success(f"Great balance — only a {gap:.0f}% gap.")
                elif gap <= 25:
                    st.warning(f"A bit uneven — {gap:.0f}% gap. Consider rebalancing a few tasks.")
                else:
                    st.error(f"Big imbalance — {gap:.0f}% gap. The Transfer tab can help share the load.")

        # Category breakdown
        with right:
            st.subheader("By category")
            cat_rows = []
            for _, row in df.iterrows():
                pts = float(row["points"])
                if row["owner"] == a:
                    cat_rows.append({"Category": row["category"], "Partner": a, "Points": pts})
                elif row["owner"] == b:
                    cat_rows.append({"Category": row["category"], "Partner": b, "Points": pts})
                elif row["owner"] == "Shared":
                    cat_rows.append({"Category": row["category"], "Partner": a, "Points": pts / 2})
                    cat_rows.append({"Category": row["category"], "Partner": b, "Points": pts / 2})
                else:
                    cat_rows.append({"Category": row["category"], "Partner": "Unassigned", "Points": pts})
            cat_df = pd.DataFrame(cat_rows)
            if cat_df.empty:
                st.info("No data yet.")
            else:
                fig2 = px.bar(
                    cat_df.groupby(["Category", "Partner"], as_index=False)["Points"].sum(),
                    x="Category",
                    y="Points",
                    color="Partner",
                    barmode="stack",
                    color_discrete_map={a: "#4C9AFF", b: "#FF8B94", "Unassigned": "#B0BEC5"},
                )
                fig2.update_layout(height=380, margin=dict(t=10, b=10, l=10, r=10), xaxis_tickangle=-25)
                st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        st.subheader("Who owns what")
        view = df.copy()
        view = view[["name", "category", "points", "frequency", "owner"]]
        view.columns = ["Task", "Category", "Points", "Frequency", "Owner"]
        st.dataframe(view, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Tasks tab
# ---------------------------------------------------------------------------
with tab_tasks:
    st.subheader("Manage your tasks")
    st.caption(
        "Tick the tasks you currently do, adjust points so heavier tasks weigh more, "
        "and assign each to a partner or mark as Shared."
    )

    # Add new task
    with st.expander("➕ Add a custom task"):
        with st.form("add_task_form", clear_on_submit=True):
            cols = st.columns([3, 2, 1, 2, 2])
            new_name = cols[0].text_input("Task name")
            categories = sorted({t["category"] for t in state["tasks"]} | {"Custom"})
            new_cat = cols[1].selectbox("Category", categories)
            new_pts = cols[2].number_input("Points", min_value=1, max_value=10, value=3)
            new_freq = cols[3].selectbox(
                "Frequency", ["Daily", "Weekly", "Monthly", "As needed", "Ongoing"]
            )
            new_owner = cols[4].selectbox("Owner", owner_options())
            submitted = st.form_submit_button("Add task", use_container_width=True)
            if submitted and new_name.strip():
                state["tasks"].append(
                    _new_task(new_name.strip(), new_cat, int(new_pts), new_freq, new_owner)
                )
                st.success(f"Added '{new_name}'")
                st.rerun()

    # Filter
    df = tasks_df()
    if not df.empty:
        cats = ["All"] + sorted(df["category"].unique().tolist())
        owners = ["All"] + owner_options()
        fc1, fc2, fc3 = st.columns([2, 2, 4])
        cat_filter = fc1.selectbox("Filter by category", cats)
        owner_filter = fc2.selectbox("Filter by owner", owners)
        search = fc3.text_input("Search", placeholder="Search task names...")

        filtered_ids = []
        for t in state["tasks"]:
            if cat_filter != "All" and t["category"] != cat_filter:
                continue
            if owner_filter != "All" and t["owner"] != owner_filter:
                continue
            if search and search.lower() not in t["name"].lower():
                continue
            filtered_ids.append(t["id"])

        st.write(f"Showing {len(filtered_ids)} of {len(state['tasks'])} tasks")

        # Edit each task inline
        for t in state["tasks"]:
            if t["id"] not in filtered_ids:
                continue
            with st.container(border=True):
                cols = st.columns([3, 2, 1, 2, 2, 1])
                t["name"] = cols[0].text_input("Task", value=t["name"], key=f"name_{t['id']}", label_visibility="collapsed")
                t["category"] = cols[1].text_input("Category", value=t["category"], key=f"cat_{t['id']}", label_visibility="collapsed")
                t["points"] = cols[2].number_input(
                    "Pts", min_value=1, max_value=10, value=int(t["points"]),
                    key=f"pts_{t['id']}", label_visibility="collapsed",
                )
                t["frequency"] = cols[3].selectbox(
                    "Frequency",
                    ["Daily", "Weekly", "Monthly", "As needed", "Ongoing"],
                    index=["Daily", "Weekly", "Monthly", "As needed", "Ongoing"].index(t["frequency"])
                    if t["frequency"] in ["Daily", "Weekly", "Monthly", "As needed", "Ongoing"] else 0,
                    key=f"freq_{t['id']}", label_visibility="collapsed",
                )
                opts = owner_options()
                t["owner"] = cols[4].selectbox(
                    "Owner",
                    opts,
                    index=opts.index(t["owner"]) if t["owner"] in opts else len(opts) - 1,
                    key=f"own_{t['id']}", label_visibility="collapsed",
                )
                if cols[5].button("🗑️", key=f"del_{t['id']}", help="Delete"):
                    state["tasks"] = [x for x in state["tasks"] if x["id"] != t["id"]]
                    st.rerun()
    else:
        st.info("No tasks yet. Add a custom one above or reset to load the default list.")


# ---------------------------------------------------------------------------
# Transfer tab
# ---------------------------------------------------------------------------
with tab_transfer:
    st.subheader("Transfer a task")
    st.caption("Hand a task over to your partner and leave a short message so you're on the same page.")

    a, b = state["partner_a"], state["partner_b"]
    df = tasks_df()
    if df.empty:
        st.info("Add some tasks first.")
    else:
        with st.form("transfer_form", clear_on_submit=True):
            task_map = {f"{t['name']}  (owner: {t['owner']})": t["id"] for t in state["tasks"]}
            chosen = st.selectbox("Which task?", list(task_map.keys()))
            new_owner = st.selectbox("Transfer to", owner_options())
            message = st.text_area("Message to your partner (optional)", placeholder="e.g. Could you take this for the next two weeks? I'm slammed at work.")
            confirmed = st.form_submit_button("Transfer task", use_container_width=True)
            if confirmed:
                task_id = task_map[chosen]
                old_owner = None
                for t in state["tasks"]:
                    if t["id"] == task_id:
                        old_owner = t["owner"]
                        t["owner"] = new_owner
                        break
                state["transfers"].append(
                    {
                        "task": chosen.split("  (owner")[0],
                        "from": old_owner,
                        "to": new_owner,
                        "message": message,
                        "at": datetime.utcnow().isoformat(),
                    }
                )
                if message.strip():
                    state["messages"].append(
                        {
                            "author": "Transfer",
                            "text": f"📦 Transferred '{chosen.split('  (owner')[0]}' from {old_owner} → {new_owner}. Note: {message}",
                            "at": datetime.utcnow().isoformat(),
                        }
                    )
                st.success(f"Transferred to {new_owner}")

        st.divider()
        st.subheader("Recent transfers")
        if not state["transfers"]:
            st.caption("No transfers yet.")
        else:
            for tr in reversed(state["transfers"][-10:]):
                ts = datetime.fromisoformat(tr["at"]).strftime("%d %b %Y · %H:%M")
                st.markdown(
                    f"- **{tr['task']}** — {tr['from']} → {tr['to']}  "
                    f"<span class='pill'>{ts}</span>  "
                    + (f"<br>💬 _{tr['message']}_" if tr["message"] else ""),
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Chat & Notes tab
# ---------------------------------------------------------------------------
with tab_chat:
    st.subheader("Couple chat & notes")
    st.caption("A simple shared space for quick check-ins about the household.")

    a, b = state["partner_a"], state["partner_b"]
    with st.form("chat_form", clear_on_submit=True):
        author = st.selectbox("From", [a, b])
        text = st.text_area("Message", placeholder="Anything you want to flag, appreciate, or plan together...")
        submitted = st.form_submit_button("Send", use_container_width=True)
        if submitted and text.strip():
            state["messages"].append(
                {"author": author, "text": text.strip(), "at": datetime.utcnow().isoformat()}
            )
            st.rerun()

    if not state["messages"]:
        st.info("No messages yet — start the conversation.")
    else:
        for m in reversed(state["messages"][-50:]):
            ts = datetime.fromisoformat(m["at"]).strftime("%d %b · %H:%M")
            with st.chat_message("user" if m["author"] == a else "assistant"):
                st.markdown(f"**{m['author']}**  ·  _{ts}_")
                st.write(m["text"])


# ---------------------------------------------------------------------------
# Tips tab
# ---------------------------------------------------------------------------
with tab_tips:
    st.subheader("How to use Share the Load")
    st.markdown(
        """
1. **Set up your household** — add both partners' names in the sidebar.
2. **Walk through the task list together** — tick the ones you do, add custom ones, and adjust points to reflect how much mental energy each one really takes (1 = trivial, 10 = exhausting).
3. **Assign owners honestly** — including emotional and invisible tasks like "remembering birthdays" or "checking in emotionally".
4. **Check the dashboard** — is the split close to 50/50? Are there categories one partner shoulders alone?
5. **Use Transfer to rebalance** — pick a task, choose the new owner, and leave a short note so your partner knows the context.
6. **Talk regularly** — use Chat & Notes for quick check-ins. Even a "thanks for handling X this week" goes a long way.
7. **Save your data** — hit Save in the sidebar (or download the JSON) so your setup persists between sessions.

#### Why points matter
Not every task carries the same load. "Taking out the bins" (1 pt) is not the same as "Organising the family calendar" (5 pts). Points let you capture invisible labour that often goes unseen.

#### Try a monthly check-in
Once a month, open Share the Load together, look at the dashboard, and rebalance anything that feels off. Small adjustments early prevent resentment later.
        """
    )
