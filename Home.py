import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(page_title="Spotify Multi-Dashboard", page_icon="🎶", layout="wide")

# --- Sidebar Navigation ---
st.sidebar.image("https://i.pinimg.com/736x/31/4c/22/314c22bbaf15c9b99b6f0bc42ae88d25.jpg", use_column_width=True)


# --- Welcome Message and Image ---
st.markdown("<h1 style='text-align: center; color: #1DB954;'>🎧 Welcome to the Spotify Data Portal</h1>", unsafe_allow_html=True)
st.markdown("##### Analyze, Explore and Compare Spotify Tracks Data from Different Sources!")

st.markdown("""
    #### 📌 About This Project:
    - This multi-page Streamlit dashboard explores Spotify track-level data from two sources:
        - 🟢 Kaggle (official dataset)
        - 🔵 Web-Scraped Spotify Data
    - It provides rich visualizations, filters, and interactive analytics.

    #### 🚀 What You Can Do:
    - Navigate to **Kaggle or Scraped Dashboards** for independent analysis.
    - Visit the **Comparison Dashboard** to explore trends and differences across datasets.
    - View raw data, top artists, popularity patterns, album releases and more.

    #### 🔧 Tech Stack:
    - Python | Pandas | Streamlit | Plotly | WordCloud | Matplotlib

    #### 👨‍💻 Developer:
    - *Built with ❤️ by Komal*

    """)



