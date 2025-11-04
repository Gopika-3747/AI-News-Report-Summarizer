import streamlit as st
import os
from one import scrape_sportingnews, prepare_data, summarize

st.set_page_config(page_title="Sports News Dashboard", page_icon="🏟️", layout="centered")

st.title("Sports News Dashboard")
st.caption("Get concise, up-to-date summaries of top sports news.")

placeholder = st.empty()

col1, col2 = st.columns([1, 3])
with col1:
    refresh_clicked = st.button("Get latest updates", type="primary", use_container_width=True)
with col2:
    st.write("")

def render_summary_from_file(path: str) -> bool:
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "r", encoding="utf-8") as f:
            summary_text = f.read()
        st.markdown(summary_text)
        return True
    return False

SUMMARY_PATH = "summary.md"

if refresh_clicked:
    with st.spinner("Scraping latest articles and generating summary... This may take a minute."):
        try:
            scrape_sportingnews()
            content = prepare_data("scraped_articles.csv")
            generated = summarize(content)
            with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
                f.write(generated)
            st.success("Updated to the latest news.")
            st.markdown(generated)
        except Exception as e:
            st.error(f"Failed to fetch latest updates: {e}")
            st.info("Showing the most recent available summary instead.")
            if not render_summary_from_file(SUMMARY_PATH):
                st.warning("No existing summary found. Please try fetching updates again.")
else:
    if not render_summary_from_file(SUMMARY_PATH):
        st.info("No saved summary found yet. Click 'Get latest updates' to generate one.")
