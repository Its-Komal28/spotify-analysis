from dotenv import load_dotenv
import os
import base64
from requests import post,get
import json
import csv

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":"+ client_secret
    auth_bytes= auth_string.encode("utf-8")
    auth_base64=str(base64.b64encode(auth_bytes),"utf8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic "+ auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"grant_type": "client_credentials"}
    result=post(url,headers=headers,data=data)
    json_result=json.loads(result.content)
    token=json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name, limit=1): # Add limit parameter with default
    url="https://api.spotify.com/v1/search"
    headers= get_auth_header(token)
    query=f"?q={artist_name}&type=artist&limit={limit}" # Use the limit parameter

    query_url= url + query
    result=get(query_url, headers=headers)
    result.raise_for_status() # Add this for better error handling
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print(f"No artist with name '{artist_name}' exists...")
        return [] # Return an empty list if no artists found
    return json_result # Return the list of artists, not just the first one
    
    

def get_songs_by_artist(token,artist_id):
    url=f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers=get_auth_header(token)
    result=get(url,headers=headers)
    json_result= json.loads(result.content)["tracks"]
    return json_result


token = get_token()
all_songs = []
artist_search_query = "pop" # Example: search for "pop" artists
artist_limit_per_search = 50 # Max limit for artist search in one query
current_offset = 0 # For potential future pagination of artist search if needed

print(f"Attempting to collect up to 1000 songs...")

# Loop to continuously search for artists and collect songs until 1000 are found
while len(all_songs) < 1000:
    # Search for a batch of artists
    # Note: You might need a more sophisticated way to get unique artists
    # across multiple searches (e.g., changing 'artist_search_query' or using offsets).
    # For simplicity, this example just uses one broad query.
    artists = search_for_artist(token, artist_search_query, limit=artist_limit_per_search)

    if not artists:
        print("No more artists found or initial search failed. Breaking loop.")
        break # Exit if no artists are found

    for artist in artists:
        artist_id = artist["id"]
        artist_name = artist["name"]
        print(f"Fetching top tracks for: {artist_name} (Current songs: {len(all_songs)})")

        songs_from_artist = get_songs_by_artist(token, artist_id)

        for song in songs_from_artist:
            if len(all_songs) < 1000:
                all_songs.append(song)
            else:
                break # Stop adding songs if 1000 is reached

        if len(all_songs) >= 1000:
            break # Stop processing artists if 1000 songs are collected

    # If after processing a batch of artists, we still don't have 1000 songs,
    # you might need to adjust the 'artist_search_query' or implement
    # more advanced pagination for artist search (e.g., by increasing 'current_offset').
    # For this example, we'll break if we can't easily hit 1000 from one broad search.
    if len(all_songs) < 1000:
        print(f"Collected {len(all_songs)} songs so far. Trying next batch or adjusting query.")
        # To get more, you would typically change artist_search_query (e.g., "rock", "jazz")
        break 

# Replace the 'songs' variable with 'all_songs' for CSV writing
songs_to_write = all_songs

# Define the CSV file name
csv_file_name = "spotify_songs_1000_entries.csv"

# Open the CSV file in write mode
with open(csv_file_name, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # Write the header row
    writer.writerow(["Song Number", "Song Name", "Artist Name", "Album Name", "Release Date", "Popularity"])

    # Write each song's data to the CSV
    for idx, song in enumerate(songs_to_write): # Use songs_to_write (all_songs) here
        song_name = song.get("name", "N/A")
        # Safely access artist name
        artist_name = song["artists"][0]["name"] if song.get("artists") and song["artists"] else "N/A"
        # Safely access album name and release date
        album_name = song["album"]["name"] if song.get("album") else "N/A"
        release_date = song["album"]["release_date"] if song.get("album") else "N/A"
        popularity = song.get("popularity", "N/A")

        writer.writerow([idx + 1, song_name, artist_name, album_name, release_date, popularity])

print(f"\nSuccessfully saved {len(songs_to_write)} songs to {csv_file_name}")
if len(songs_to_write) < 1000:
    print(f"Note: Could only find {len(songs_to_write)} unique songs with the current search strategy.")
    



