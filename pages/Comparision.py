import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Setup ---
st.set_page_config(page_title="Spotify Dataset Comparison", layout="wide")
st.title("📊 Spotify Dataset Comparison: Scraped vs Kaggle")

# --- Load Data ---
@st.cache_data
def load_data():
    df_scraped = pd.read_csv(r'C:\Users\Savy\OneDrive\Desktop\spotify\imp\spotify-analysis\data\spotify_scrap.csv')
    df_kaggle = pd.read_csv(r'C:\Users\Savy\OneDrive\Desktop\spotify\imp\spotify-analysis\data\dataset.csv')
    return df_scraped, df_kaggle

df_scraped, df_kaggle = load_data()

# --- Rename & Normalize ---
df_scraped = df_scraped.rename(columns={
    'Song Name': 'track_name',
    'Artist Name': 'artists',
    'Album Name': 'album',
    'Release Date': 'release_date',
    'Popularity': 'popularity'
})
df_scraped['Source'] = 'Scraped'
df_kaggle['Source'] = 'Kaggle'

# Ensure popularity is numeric
df_scraped['popularity'] = pd.to_numeric(df_scraped['popularity'], errors='coerce')
df_kaggle['popularity'] = pd.to_numeric(df_kaggle['popularity'], errors='coerce')

# Add placeholder genre if missing
if 'track_genre' not in df_scraped.columns:
    df_scraped['track_genre'] = 'unknown'

# Combine for shared analysis
common_cols = list(set(df_scraped.columns) & set(df_kaggle.columns))
df_combined = pd.concat([df_scraped[common_cols], df_kaggle[common_cols]], ignore_index=True)

# --- Summary Table ---
st.subheader("🔍 Summary Statistics")
summary = pd.DataFrame({
    "Total Tracks": [len(df_scraped), len(df_kaggle)],
    "Unique Artists": [df_scraped['artists'].nunique(), df_kaggle['artists'].nunique()],
    "Avg Popularity": [df_scraped['popularity'].mean(), df_kaggle['popularity'].mean()],
    "Top Genre": [
        df_scraped['track_genre'].mode()[0] if not df_scraped['track_genre'].isna().all() else "N/A",
        df_kaggle['track_genre'].mode()[0] if not df_kaggle['track_genre'].isna().all() else "N/A"
    ]
}, index=["Scraped", "Kaggle"])
st.dataframe(summary)

# --- Genre Distribution (Relative % Bar) ---
st.subheader("🎼 Genre Distribution (Top 10 by Source, % Share)")

def top_genres_percent(df, source_label):
    genre_counts = df['track_genre'].value_counts(normalize=True).head(10) * 100
    return pd.DataFrame({'Genre': genre_counts.index, 'Percentage': genre_counts.values, 'Source': source_label})

genre_scraped = top_genres_percent(df_scraped, "Scraped")
genre_kaggle = top_genres_percent(df_kaggle, "Kaggle")
genre_df = pd.concat([genre_scraped, genre_kaggle])

fig_genre = px.bar(
    genre_df,
    x="Genre",
    y="Percentage",
    color="Source",
    barmode="group",
    title="Top Genres by Percentage Share",
    template="plotly_white"
)
st.plotly_chart(fig_genre, use_container_width=True)

# --- Popularity Comparison (Box Plot) ---
st.subheader("🌟 Popularity Distribution")
fig_pop = px.box(
    df_combined,
    x="Source",
    y="popularity",
    title="Popularity Distribution (Box Plot)",
    template="plotly_white"
)
st.plotly_chart(fig_pop, use_container_width=True)

# --- Optional Audio Feature Comparison ---
audio_features = ['danceability', 'energy', 'tempo', 'valence']
available = [f for f in audio_features if f in df_scraped.columns and f in df_kaggle.columns]

if available:
    st.subheader("🎧 Audio Feature Comparison")
    feature = st.selectbox("Select Audio Feature", available)

    df_feat = pd.concat([
        df_scraped[[feature]].assign(Source="Scraped"),
        df_kaggle[[feature]].assign(Source="Kaggle")
    ])

    fig_feat = px.box(
        df_feat,
        x="Source",
        y=feature,
        title=f"{feature.title()} Comparison (Box Plot)",
        template="plotly_white"
    )
    st.plotly_chart(fig_feat, use_container_width=True)
else:
    st.info("No shared audio features in both datasets.")

# --- Raw Data (Optional Expanders) ---
st.subheader("📂 Raw Data (First 10 Rows)")
with st.expander("View Scraped Dataset"):
    st.dataframe(df_scraped.head(10))
with st.expander("View Kaggle Dataset"):
    st.dataframe(df_kaggle.head(10))

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color: gray;'>Built with ❤️ using Streamlit</p>", unsafe_allow_html=True)
