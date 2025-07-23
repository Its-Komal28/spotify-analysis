import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def add_bg_image():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://img.freepik.com/free-photo/3d-colourful-particle-waves-background-design_1048-17733.jpg?semt=ais_hybrid&w=740");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_image()

# --- Page Configuration ---
st.set_page_config(
    page_title="Spotify Data Analysis",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading and Preprocessing ---

@st.cache_data
def load_data():
    """
    Loads the Spotify dataset ('dataset.csv'), performs initial cleaning and preprocessing
    based on the provided column names.
    """
    try:
        df = pd.read_csv(r'C:\Users\Savy\OneDrive\Desktop\spotify\imp\spotify-analysis\data\dataset.csv')
    except FileNotFoundError:
        st.error("Error: 'dataset.csv' not found. Please ensure the dataset is in the same directory as 'app.py'.")
        st.stop() 

    # --- Basic Data Cleaning ---
   
    initial_rows = df.shape[0]
    df.dropna(subset=['track_name', 'artists', 'popularity', 'track_genre'], inplace=True)
    
    # Ensure 'popularity' is numeric
    df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
    df.dropna(subset=['popularity'], inplace=True) # Drop any rows where popularity couldn't be converted

    # Handle duplicates (e.g., based on track name and artist)
    df.drop_duplicates(subset=['track_name', 'artists'], inplace=True)

    
    if 'artists' in df.columns:
        df['artists'] = df['artists'].apply(lambda x: x.strip("[]").replace("'", "").split(", ") if isinstance(x, str) else [])
       
        df_exploded = df.explode('artists')
        df_exploded['artists'] = df_exploded['artists'].str.strip() # Remove any leading/trailing whitespace
    else:
        st.warning("No 'artists' column found. Artist-based analysis will be limited.")
        df_exploded = df.copy() # Create a copy to avoid errors later

    # Clean 'track_genre' column (ensure consistency, handle potential leading/trailing spaces)
    if 'track_genre' in df.columns:
        df['track_genre'] = df['track_genre'].astype(str).str.strip().str.lower()
        df_exploded['track_genre'] = df_exploded['track_genre'].astype(str).str.strip().str.lower()
    else:
        st.warning("No 'track_genre' column found. Genre-based analysis will be limited.")

    return df, df_exploded # Return both original and exploded for different analyses

# Load the data
df_original, df_exploded_artists = load_data()


audio_features = [
    'danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
    'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms'
]
# Filter out features that might not exist in the loaded data (safety check)
audio_features = [f for f in audio_features if f in df_original.columns]

# --- Streamlit App Title and Introduction ---
st.title("🎵 Spotify Data Analysis Dashboard")

st.markdown("""
Welcome to the interactive Spotify Data Analysis Dashboard! Explore audio features,
popularity, and genre insights from your Spotify dataset.
Use the sidebar to filter and customize your analysis.
""")

# --- Sidebar Filters ---

st.sidebar.header("📊 Filters & Controls")

# Popularity Slider
popularity_range = st.sidebar.slider(
    "Select Popularity Range (0-100)",
    min_value=0,
    max_value=100,
    value=(0, 100)
)
df_filtered = df_original[
    (df_original['popularity'] >= popularity_range[0]) &
    (df_original['popularity'] <= popularity_range[1])
].copy()

# Genre Multiselect Filter
all_genres = sorted(df_original['track_genre'].unique().tolist()) if 'track_genre' in df_original.columns else []
selected_genres = st.sidebar.multiselect(
    "Select Genres",
    options=all_genres,
    default=all_genres
)

if selected_genres:
    df_filtered = df_filtered[df_filtered['track_genre'].isin(selected_genres)].copy()
else:
    st.sidebar.info("No genres selected. Showing all tracks within popularity range.")


# Selectbox for Audio Feature Distribution
selected_feature_dist = st.sidebar.selectbox(
    "Select Audio Feature for Distribution",
    audio_features
)

# Selectboxes for Scatter Plot
st.sidebar.subheader("Scatter Plot Features")
x_feature = st.sidebar.selectbox("X-axis Feature", audio_features, index=audio_features.index('danceability') if 'danceability' in audio_features else 0)
y_feature = st.sidebar.selectbox("Y-axis Feature", audio_features, index=audio_features.index('energy') if 'energy' in audio_features else 0)



# Row 1: Key Metrics and Data Sample
st.subheader("Key Metrics & Filtered Data Sample")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Tracks (Filtered)", f"{df_filtered.shape[0]:,}")
with col2:
    if 'popularity' in df_filtered.columns:
        st.metric("Average Popularity", f"{df_filtered['popularity'].mean():.2f}")
    else:
        st.metric("Average Popularity", "N/A")
with col3:
    if 'duration_ms' in df_filtered.columns:
        st.metric("Avg. Track Duration (min)", f"{(df_filtered['duration_ms'] / 60000).mean():.2f}")
    else:
        st.metric("Avg. Track Duration (min)", "N/A")

st.markdown("---")
st.write("### Filtered Data Preview")
st.dataframe(df_filtered.head(10)) # Display first 10 rows of filtered data

st.markdown("---")

# Row 2: Audio Feature Distribution and Top Genres
col_dist, col_genres = st.columns(2)

with col_dist:
    st.subheader(f"Distribution of {selected_feature_dist.replace('_', ' ').title()}")
    if selected_feature_dist in df_filtered.columns:
        fig_dist = px.histogram(
            df_filtered,
            x=selected_feature_dist,
            nbins=30,
            title=f'Distribution of {selected_feature_dist.replace("_", " ").title()}',
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_dist.update_layout(xaxis_title=selected_feature_dist.replace("_", " ").title(), yaxis_title="Number of Tracks")
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.warning(f"'{selected_feature_dist}' column not found in data.")

with col_genres:
    st.subheader("Top Genres by Track Count")
    if 'track_genre' in df_filtered.columns:
        genre_counts = df_filtered['track_genre'].value_counts().head(10).reset_index()
        genre_counts.columns = ['Genre', 'Count']
        fig_genres = px.bar(
            genre_counts,
            x='Count',
            y='Genre',
            orientation='h',
            title='Top 10 Genres by Track Count',
            template="plotly_white",
            color='Count',
            color_continuous_scale=px.colors.sequential.Plasma
        )
        fig_genres.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_genres, use_container_width=True)
    else:
        st.warning("Genre analysis not available: 'track_genre' column missing.")

st.markdown("---")

# Row 3: Correlation Heatmap and Scatter Plot
col_corr, col_scatter = st.columns(2)

with col_corr:
    st.subheader("Correlation Heatmap of Audio Features")
    # Select only numeric columns for correlation
    numeric_df = df_filtered[audio_features]
    if not numeric_df.empty:
        corr_matrix = numeric_df.corr()
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=px.colors.sequential.Viridis,
            title="Correlation Matrix of Audio Features"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("No numeric audio features found for correlation heatmap in the filtered data.")

with col_scatter:
    st.subheader(f"Scatter Plot: {x_feature.replace('_', ' ').title()} vs. {y_feature.replace('_', ' ').title()}")
    if x_feature in df_filtered.columns and y_feature in df_filtered.columns:
        fig_scatter = px.scatter(
            df_filtered,
            x=x_feature,
            y=y_feature,
            hover_name="track_name", # Show track name on hover
            hover_data=['artists', 'popularity', 'track_genre'], # Add more info on hover
            title=f'{x_feature.replace("_", " ").title()} vs. {y_feature.replace("_", " ").title()}',
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_scatter.update_layout(
            xaxis_title=x_feature.replace("_", " ").title(),
            yaxis_title=y_feature.replace("_", " ").title()
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning(f"Selected features '{x_feature}' or '{y_feature}' not found in data.")

st.markdown("---")

# Row 4: Top Artists/Tracks
st.subheader("Top Artists and Tracks")
col_top_artists, col_top_tracks = st.columns(2)

# Filter df_exploded_artists based on current filters
df_exploded_artists_filtered = df_exploded_artists[
    (df_exploded_artists['popularity'] >= popularity_range[0]) &
    (df_exploded_artists['popularity'] <= popularity_range[1])
].copy()

if selected_genres and 'track_genre' in df_exploded_artists_filtered.columns:
    df_exploded_artists_filtered = df_exploded_artists_filtered[
        df_exploded_artists_filtered['track_genre'].isin(selected_genres)
    ].copy()


if 'artists' in df_exploded_artists_filtered.columns and 'popularity' in df_exploded_artists_filtered.columns:
    with col_top_artists:
        st.write("#### Top 10 Artists by Average Popularity (Filtered)")
        top_artists = df_exploded_artists_filtered.groupby('artists')['popularity'].mean().sort_values(ascending=False).head(10).reset_index()

        if not top_artists.empty:
            fig_top_artists = px.bar(
                top_artists,
                x='popularity',
                y='artists',
                orientation='h',
                title='Top 10 Artists by Average Popularity',
                template="plotly_white",
                color='popularity',
                color_continuous_scale=px.colors.sequential.Plasma
            )
            fig_top_artists.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top_artists, use_container_width=True)
        else:
            st.info("No artists found for the selected filters.")

    with col_top_tracks:
        st.write("#### Top 10 Most Popular Tracks (Filtered)")
        top_tracks = df_filtered.sort_values(by='popularity', ascending=False).head(10)
        if not top_tracks.empty:
            st.dataframe(top_tracks[['track_name', 'artists', 'popularity', 'track_genre']])
        else:
            st.info("No tracks found for the selected filters.")
else:
    st.info("Top artists/tracks analysis not available: Missing 'artists' or 'popularity' column.")

st.markdown("---")
st.markdown("### Raw Data (Full Dataset)")
if st.checkbox("Show raw data"):
    st.dataframe(df_original)


