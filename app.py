import json
from datetime import datetime
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Daily Dashboard", page_icon="📊", layout="centered")

DATA_FILE = Path(__file__).parent / "data.json"
SHEET_CSV_URL = st.secrets.get("SHEET_CSV_URL", "")
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", "")


@st.cache_data(ttl=15)
def load_decisions() -> pd.DataFrame:
    cols = ["timestamp", "creative_id", "creative", "decision"]
    if not SHEET_CSV_URL:
        return pd.DataFrame(columns=cols)
    try:
        r = requests.get(SHEET_CSV_URL, timeout=10)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df[cols]
    except Exception:
        return pd.DataFrame(columns=cols)


@st.cache_data(ttl=60)
def load_creatives() -> list:
    if not WEBHOOK_URL:
        return []
    try:
        r = requests.get(WEBHOOK_URL, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def submit_decision(creative_id: str, creative_title: str, decision: str) -> bool:
    if not WEBHOOK_URL:
        st.error("Webhook URL not configured. Add WEBHOOK_URL in Streamlit secrets.")
        return False
    try:
        payload = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "creative_id": creative_id,
            "creative": creative_title,
            "decision": decision,
        }
        r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        return r.ok
    except Exception as e:
        st.error(f"Could not record decision: {e}")
        return False


with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

st.title("Daily Dashboard")
st.caption(f"Updated: {data.get('date', '—')}")

st.subheader("What's happening")
updates = data.get("updates", [])
if not updates:
    st.info("No updates today.")
else:
    for u in updates:
        with st.container(border=True):
            st.markdown(f"**{u.get('category', 'Update')}**")
            st.write(u.get("text", ""))

st.subheader("Creatives pending approval")
creatives = load_creatives()
decisions = load_decisions()
decided_by_id = (
    {row["creative_id"]: row for _, row in decisions.iterrows() if row["creative_id"]}
    if not decisions.empty else {}
)

col_refresh, _ = st.columns([1, 4])
if col_refresh.button("🔄 Refresh from Drive"):
    load_creatives.clear()
    load_decisions.clear()
    st.rerun()

if not creatives:
    st.info("Nothing in the pending Drive folder right now.")
else:
    for c in creatives:
        cid = c.get("id", "")
        title = c.get("title", "Untitled")
        with st.container(border=True):
            if c.get("thumbnail"):
                try:
                    st.image(c["thumbnail"], use_container_width=True)
                except Exception:
                    st.caption("(thumbnail couldn't load — open in Drive)")
            st.markdown(f"**{title}**")
            if c.get("description"):
                st.write(c["description"])
            if c.get("view_url"):
                st.markdown(f"[Open in Drive →]({c['view_url']})")

            if cid in decided_by_id:
                d = decided_by_id[cid]
                icon = "✅" if d["decision"] == "Approved" else "❌"
                st.success(f"{icon} {d['decision']} — {d['timestamp']}")
            else:
                col1, col2 = st.columns(2)
                if col1.button("✅ Approve", key=f"a_{cid}", use_container_width=True, type="primary"):
                    if submit_decision(cid, title, "Approved"):
                        load_decisions.clear()
                        st.rerun()
                if col2.button("❌ Disapprove", key=f"d_{cid}", use_container_width=True):
                    if submit_decision(cid, title, "Disapproved"):
                        load_decisions.clear()
                        st.rerun()

st.subheader("Recent decisions")
if decisions.empty:
    st.caption("No decisions logged yet.")
else:
    recent = decisions.tail(15).iloc[::-1].reset_index(drop=True)
    st.dataframe(
        recent[["timestamp", "creative", "decision"]],
        use_container_width=True,
        hide_index=True,
    )
