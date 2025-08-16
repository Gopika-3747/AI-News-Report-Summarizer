import streamlit as st

with open("summary.md", "r", encoding="utf-8") as f:
    summary = f.read()

st.markdown(summary)
