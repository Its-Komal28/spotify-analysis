import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image

# Page configuration
st.set_page_config(page_title="Spotify Dashboard",  layout="wide")
# Background image CSS
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://img.freepik.com/free-photo/artistic-blurry-colorful-wallpaper-background_58702-10253.jpg?semt=ais_hybrid&w=740");
    background-size: cover;
    background-position: top left;
    background-repeat: no-repeat;
    background-attachment: fixed;
}
[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0);
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\Savy\OneDrive\Desktop\spotify\imp\spotify-analysis\data\spotify_scrap.csv")
    df.dropna(subset=['Song Name', 'Artist Name', 'Album Name', 'Release Date', 'Popularity'], inplace=True)
    df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
    df.dropna(subset=['Release Date'], inplace=True)
    df['Release Year'] = df['Release Date'].dt.year
    return df

df = load_data()

# Sidebar UI
try:
    st.sidebar.image("https://miro.medium.com/v2/resize:fit:1400/1*DzANpcOwzOBxjbFZA0L27g.jpeg", use_column_width=True)
except:
    st.sidebar.markdown("🎵 Spotify Dashboard")

st.sidebar.title("Spotify Dashboard")
menu = st.sidebar.radio("Go to", ["Home", "Popularity Insights", "Album Analysis", "Time Trends", "Word Cloud", "Raw Data"])

# Sidebar Filters (Release Year)
min_year = int(df['Release Year'].min())
max_year = int(df['Release Year'].max())
year_range = st.sidebar.slider("Filter by Release Year", min_year, max_year, (min_year, max_year))
df_filtered = df[(df['Release Year'] >= year_range[0]) & (df['Release Year'] <= year_range[1])]

# Sidebar Filters (Artist — now optional)
artist_options = sorted(df_filtered['Artist Name'].unique())
selected_artists = st.sidebar.multiselect("Select Artists (optional)", artist_options)

if selected_artists:
    df_filtered = df_filtered[df_filtered['Artist Name'].isin(selected_artists)]

# --- Home ---
if menu == "Home":
    st.markdown("<h1 style='text-align: center;'>🎵 Welcome to the Spotify Music Explorer 🎵</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; font-size: 18px;'>
        🎧 Explore your favorite songs, albums, and artists<br>
        📈 Dive deep into popularity trends<br>
        🎨 Discover music patterns with interactive visuals<br><br>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])  # left: text & metrics, right: image

    with col_left:
        st.write(f"🎯 Showing **{df_filtered.shape[0]}** songs out of **{df.shape[0]}** total songs.")

        col1, col2, col3 = st.columns(3)
        col1.metric("🎶 Total Songs", f"{df_filtered.shape[0]}")
        col2.metric("🧑‍🎤 Unique Artists", df_filtered['Artist Name'].nunique())
        col3.metric("🔥 Avg Popularity", f"{df_filtered['Popularity'].mean():.2f}")

    with col_right:
        st.image("https://c.ndtvimg.com/2025-04/ogp7i0fc_spotify-erhht-im-sommer-2025-erneut-die-preise-jhrlich-wird-das-zur-regel_625x300_30_April_25.jpg?im=FitAndFill,algorithm=dnn,width=1200,height=738", use_column_width=True, caption="Spotify Vibes 🎵")


# --- Popularity Insights ---
elif menu == "Popularity Insights":
    st.subheader("Popularity Distribution")
    fig_pop = px.histogram(df_filtered, x="Popularity", nbins=20, color_discrete_sequence=px.colors.sequential.RdBu)
    fig_pop.update_layout(xaxis_title="Popularity", yaxis_title="Number of Songs")
    st.plotly_chart(fig_pop, use_container_width=True)

    st.subheader("Top 10 Songs by Popularity")
    top_songs = df_filtered.sort_values(by="Popularity", ascending=False).head(10)
    fig_top = px.bar(top_songs, x="Popularity", y="Song Name", color='Artist Name', orientation='h',
                     title="Top Songs", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_top, use_container_width=True)

# --- Album Analysis ---
elif menu == "Album Analysis":
    st.subheader("Top Albums by Song Count")
    album_counts = df_filtered['Album Name'].value_counts().head(10)
    fig_album = px.bar(x=album_counts.values, y=album_counts.index, orientation='h',
                       labels={'x': 'Number of Songs', 'y': 'Album Name'}, color_discrete_sequence=px.colors.sequential.Aggrnyl)
    st.plotly_chart(fig_album, use_container_width=True)

# --- Time Trends ---
elif menu == "Time Trends":
    st.subheader("Tracks Released per Year")
    year_counts = df_filtered['Release Year'].value_counts().sort_index()
    fig_years = px.bar(x=year_counts.index, y=year_counts.values,
                       labels={'x': 'Year', 'y': 'Number of Songs'}, color_discrete_sequence=px.colors.sequential.Cividis)
    st.plotly_chart(fig_years, use_container_width=True)

    st.subheader("Popularity Over Time")
    fig_time = px.scatter(df_filtered, x="Release Date", y="Popularity", color="Artist Name",
                          hover_data=["Song Name", "Album Name"], color_discrete_sequence=px.colors.diverging.Portland)
    st.plotly_chart(fig_time, use_container_width=True)

# --- Word Cloud ---
elif menu == "Word Cloud":
    st.subheader("Word Cloud of Song Titles")
    text = " ".join(df_filtered['Song Name'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig_wc, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig_wc)

# --- Raw Data ---
elif menu == "Raw Data":
    st.subheader("Explore Raw Dataset")
    st.dataframe(df_filtered)

# Footer
st.markdown("""
<hr style="border:0.5px solid #ccc">
<p style='text-align:center; color: gray;'>
Created with ❤️ using Streamlit | Data from Spotify
</p>
""", unsafe_allow_html=True)

