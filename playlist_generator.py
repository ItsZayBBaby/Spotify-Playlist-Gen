import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import json
from urllib.parse import urlparse, parse_qs

# ---------------------------
# ✅ Your Working Spotify Authentication (No Changes)
# ---------------------------
SPOTIPY_CLIENT_ID = "4aa946837d32453dac0d603f1e66258e"
SPOTIPY_CLIENT_SECRET = "cac0325402e74a148daeaa26c7344629"
SPOTIPY_REDIRECT_URI = "https://ho94zgrbrqziufzcy7rdtn.streamlit.app/#df314819" 

auth_manager = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-top-read playlist-modify-public playlist-modify-private",
    show_dialog=True,
    cache_path=None  # Prevents storing access tokens
)

sp = None  # Define sp globally so it can be assigned later

# ---------------------------
# 🎵 Streamlit UI: Genre-Based Playlist Generator
# ---------------------------
st.title("Genre-Based Playlist Generator")

# Check if authorization is complete
query_params = st.query_params
auth_code = query_params.get("code", None)

# ✅ Step 1: Handle Authentication (Check if the user is logged in)
if "spotify_token" not in st.session_state:
    auth_url = auth_manager.get_authorize_url()
    st.markdown(f"[Click here to authorize Spotify]({auth_url})")
    auth_code = st.query_params.get("code", None)

    if auth_code:
        try:
            token_info = auth_manager.get_access_token(auth_code, as_dict=True)
            st.session_state.spotify_token = token_info["access_token"]
        except Exception as e:
            st.error(f"⚠️ Error during authentication: {e}")
            st.stop()

# ✅ Step 2: Create Spotify Client After Login
if "spotify_token" in st.session_state:
    sp = spotipy.Spotify(auth=st.session_state.spotify_token)
    st.success("✅ Authentication successful! You can now generate playlists.")
else:
    st.stop()

# ---------------------------
# 📊 Fetch & Display User's Top Tracks (Optional)
# ---------------------------

try:
    user_profile = sp.me()
    st.write("Logged in as:", user_profile["display_name"])
except Exception as e:
    st.error(f"Error verifying user profile: {e}")
    st.stop()

if st.button("Show My Top Tracks"):
    top_tracks = sp.current_user_top_tracks(limit=10, time_range='medium_term')

    track_info_list = []
    track_ids = []  # List to store track IDs for audio features lookup

    for idx, track in enumerate(top_tracks['items']):
        track_id = track.get('id')  # Ensure we're getting the track ID
        if track_id:  # Only add non-empty IDs
            track_ids.append(track_id)

            # Get artist info to fetch genre (only from the first artist listed)
            artist_id = track['artists'][0]['id']
            artist_info = sp.artist(artist_id)
            genres = artist_info.get('genres') or ["Unknown Genre"]

            track_info = {
                "No.": idx + 1,
                "Track Name": track['name'],
                "Artist(s)": ", ".join([artist['name'] for artist in track['artists']]),
                "Album": track['album']['name'],
                "Release Date": track['album'].get('release_date', "N/A"),
                "Popularity": track['popularity'],
                "Genres": ", ".join(str(g) for g in genres),
                "Preview URL": track.get('preview_url', "No preview available"),
            }
            track_info_list.append(track_info)

    # ✅ Debugging: Ensure track_ids list is valid
    st.write("Debug - Track IDs:", track_ids)

    if not track_ids:  # If the list is empty, stop execution
        st.error("⚠️ No valid track IDs found. Cannot fetch audio features.")
        st.stop()

    # ✅ Fetch additional metadata (audio features)
    try:
        audio_features = sp.audio_features(track_ids)  # Returns a list
        for i, features in enumerate(audio_features):
            if features:
                track_info_list[i]["Tempo (BPM)"] = features.get('tempo', "N/A")
                track_info_list[i]["Valence (Mood)"] = features.get('valence', "N/A")
                track_info_list[i]["Danceability"] = features.get('danceability', "N/A")
                track_info_list[i]["Energy"] = features.get('energy', "N/A")
    except Exception as e:
        st.error(f"⚠️ Error fetching audio features: {e}")
        st.stop()

    # Convert list to DataFrame for display
    df_tracks = pd.DataFrame(track_info_list)
    
    st.subheader("🎵 My Top Tracks (With Additional Metadata)")
    st.dataframe(df_tracks)
    
    # Optionally, display album covers
    st.subheader("Album Covers")
    for track in top_tracks['items']:
        album_image_url = track['album']['images'][0]['url'] if track['album']['images'] else None
        if album_image_url:
            st.image(album_image_url, caption=f"{track['name']} - {', '.join([artist['name'] for artist in track['artists']])}", width=150)
