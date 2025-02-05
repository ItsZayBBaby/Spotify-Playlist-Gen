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

sp = None  # Define `sp` globally so it can be assigned later

# ---------------------------
# 🎵 Streamlit UI: Genre-Based Playlist Generator
# ---------------------------
st.title("🎵 Genre-Based Playlist Generator")

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

# ✅ Step 3: Fetch Valid Spotify Genres
try:
    valid_genres = sp.recommendation_genre_seeds()["genres"]
except Exception as e:
    st.error(f"⚠️ Error fetching valid genres: {e}")
    st.stop()

# ✅ Step 4: User Selects a Genre
selected_genre = st.selectbox("Select a Genre:", valid_genres)


# ✅ Step 5: Generate Playlist When Button is Clicked
if st.button("Generate Playlist"):
    # Validate Genre Selection
    if selected_genre not in valid_genres:
        st.error(f"⚠️ '{selected_genre}' is not a valid genre for recommendations.")
        st.stop()

    # ✅ Step 6: Get Recommended Tracks (Try-Except to Catch API Errors)
    try:
        recommendations = sp.recommendations(seed_genres=[selected_genre], limit=20)
        track_uris = [track["uri"] for track in recommendations["tracks"]]
    except Exception as e:
        st.error(f"⚠️ Error fetching recommendations: {e}")
        st.stop()

         # ✅ Step 7: Create a Playlist and Add Tracks
    try:
        user_id = sp.me()["id"]
        playlist_name = f"{selected_genre.capitalize()} Vibes Playlist"
        playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
        sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris)

        st.success(f"✅ Playlist '{playlist_name}' created!")
        st.write(f"👉 [Open in Spotify]({playlist['external_urls']['spotify']})")

    except Exception as e:
        st.error(f"⚠️ Error creating playlist: {e}")
        st.stop()

# ---------------------------
# 📊 Fetch & Display User's Top Tracks (Optional)
# ---------------------------
if st.button("Show My Top Tracks"):
    top_tracks = sp.current_user_top_tracks(limit=10, time_range='medium_term')

    for idx, track in enumerate(top_tracks['items']):
        st.write(f"{idx+1}. {track['name']} by {track['artists'][0]['name']}")
