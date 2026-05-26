"""
Storage layer for Share the Load.

If Supabase credentials are present (via env vars or st.secrets), use Supabase
so both partners share the same household across devices.

Otherwise fall back to a local JSON file so the app still works for development.

Supabase setup (free tier is fine):
  1. Create a project at https://supabase.com
  2. In the SQL editor, run:

        create table if not exists households (
            id text primary key,
            data jsonb not null,
            updated_at timestamp with time zone default now()
        );

  3. Add these to Streamlit secrets (or env vars):
        SUPABASE_URL = "https://<project>.supabase.co"
        SUPABASE_ANON_KEY = "<anon-key>"
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

DATA_FILE = Path("household_data.json")


def _get_secret(name: str) -> Optional[str]:
    # 1. Env var
    val = os.environ.get(name)
    if val:
        return val
    # 2. Streamlit secrets (only if streamlit is loaded and secrets.toml exists)
    try:
        import streamlit as st  # noqa: WPS433
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return None


def _supabase_client():
    url = _get_secret("SUPABASE_URL")
    key = _get_secret("SUPABASE_ANON_KEY")
    if not (url and key):
        return None
    try:
        from supabase import create_client  # type: ignore
    except ImportError:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


def using_cloud() -> bool:
    return _supabase_client() is not None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def load(household_id: str = "default") -> Optional[dict]:
    """Return the saved state for this household, or None if not found."""
    client = _supabase_client()
    if client:
        try:
            resp = client.table("households").select("data").eq("id", household_id).execute()
            rows = resp.data or []
            if rows:
                return rows[0]["data"]
            return None
        except Exception:
            return _load_local()
    return _load_local()


def save(state: dict, household_id: str = "default") -> None:
    """Persist state for this household."""
    client = _supabase_client()
    if client:
        try:
            client.table("households").upsert(
                {"id": household_id, "data": state}
            ).execute()
            return
        except Exception:
            # Fall back to local on cloud failure
            pass
    _save_local(state)


# ---------------------------------------------------------------------------
# Local file fallback
# ---------------------------------------------------------------------------
def _load_local() -> Optional[dict]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            return None
    return None


def _save_local(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))
