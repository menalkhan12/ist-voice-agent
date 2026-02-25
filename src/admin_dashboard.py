"""
Admin Dashboard for IST Admissions Voice Agent.
Run with: uv run streamlit run src/admin_dashboard.py
Shows: live call log, Master JSON viewer/editor, latency graphs.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
CALL_LOG_PATH = ROOT_DIR / "logs" / "call_log.json"
MASTER_JSON_PATH = ROOT_DIR / "data" / "99_MASTER_JSON.json"

st.set_page_config(page_title="IST Voice Agent Admin", layout="wide")
st.title("IST Admissions Voice Agent — Admin Dashboard")

# Sidebar: refresh and nav
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Call log", "Master JSON", "Latency graphs"],
    index=0,
)
if st.sidebar.button("Refresh data"):
    st.rerun()

# --- Call log ---
if page == "Call log":
    st.header("Live call / query log")
    if not CALL_LOG_PATH.exists():
        st.warning("No call log found. Run the voice agent to generate logs.")
    else:
        try:
            with open(CALL_LOG_PATH, encoding="utf-8") as f:
                log = json.load(f)
        except Exception as e:
            st.error(f"Could not load call log: {e}")
            log = []
        if not log:
            st.info("Call log is empty.")
        else:
            df = pd.DataFrame(log)
            st.dataframe(
                df[["call_start", "call_end", "stt_latency_s", "llm_latency_s", "tts_latency_s", "e2e_s", "transcript", "escalated"]],
                use_container_width=True,
                hide_index=True,
            )
            st.caption(f"Total entries: {len(log)}")

# --- Master JSON ---
if page == "Master JSON":
    st.header("Master JSON (scraped IST content)")
    if not MASTER_JSON_PATH.exists():
        st.warning("Master JSON not found.")
    else:
        try:
            with open(MASTER_JSON_PATH, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            st.error(f"Could not load JSON: {e}")
            data = {}
        pages = data.get("pages", {})
        st.write(f"**Pages in corpus:** {len(pages)}")
        url_filter = st.text_input("Filter by URL (substring)", "")
        if url_filter:
            pages = {k: v for k, v in pages.items() if url_filter.lower() in k.lower()}
        selected_url = st.selectbox("Select a page to view / edit", [""] + list(pages.keys()), index=0)
        if selected_url:
            page_data = pages[selected_url]
            title = page_data.get("title", "")
            text_blocks = page_data.get("text_blocks", [])
            text = page_data.get("text", "")
            st.subheader(title or "(No title)")
            st.write("**URL:**", selected_url)
            edited = st.text_area(
                "Edit text (one block per line or single text)",
                "\n".join(text_blocks) if text_blocks else text,
                height=300,
            )
            if st.button("Update this page in Master JSON"):
                try:
                    new_blocks = [line.strip() for line in edited.strip().split("\n") if line.strip()]
                    data["pages"][selected_url]["text_blocks"] = new_blocks
                    data["pages"][selected_url]["text"] = " ".join(new_blocks)
                    with open(MASTER_JSON_PATH, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    st.success("Saved. Restart the voice agent to reload the corpus.")
                except Exception as e:
                    st.error(str(e))
        st.divider()
        try:
            raw = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                label="Download full Master JSON",
                data=raw,
                file_name="99_MASTER_JSON.json",
                mime="application/json",
                key="dl_master",
            )
        except Exception:
            pass

# --- Latency graphs ---
if page == "Latency graphs":
    st.header("Latency over time")
    if not CALL_LOG_PATH.exists():
        st.warning("No call log found.")
    else:
        try:
            with open(CALL_LOG_PATH, encoding="utf-8") as f:
                log = json.load(f)
        except Exception as e:
            st.error(f"Could not load call log: {e}")
            log = []
        if not log:
            st.info("No data to plot.")
        else:
            df = pd.DataFrame(log)
            df["call_start"] = pd.to_datetime(df["call_start"], errors="coerce")
            df = df.dropna(subset=["call_start"]).sort_values("call_start")
            df["index"] = range(len(df))
            st.line_chart(
                df.set_index("index")[["stt_latency_s", "llm_latency_s", "tts_latency_s", "e2e_s"]],
                height=400,
            )
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg STT (s)", f"{df['stt_latency_s'].mean():.2f}")
            with col2:
                st.metric("Avg LLM (s)", f"{df['llm_latency_s'].mean():.2f}")
            with col3:
                st.metric("Avg TTS (s)", f"{df['tts_latency_s'].mean():.2f}")
            with col4:
                st.metric("Avg E2E (s)", f"{df['e2e_s'].mean():.2f}")
