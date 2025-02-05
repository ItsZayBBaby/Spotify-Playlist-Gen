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
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback/"

auth_manager = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-top-read playlist-modify-public playlist-modify-private"
    show_dialog=True
)

sp = spotipy.Spotify(auth_manager=auth_manager)

# ---------------------------
# 🎵 Streamlit UI: Genre-Based Playlist Generator
# ---------------------------
st.title("🎵 Genre-Based Playlist Generator")

# Select a genre
selected_genre = st.selectbox("Select a Genre:", ["pop", "rock", "hip-hop", "indie", "electronic", "jazz"])

if st.button("Generate Playlist"):
    recommendations = sp.recommendations(seed_genres=[selected_genre], limit=20)
    track_uris = [track['uri'] for track in recommendations['tracks']]

    # Create Playlist
    user_id = sp.me()['id']
    playlist_name = f"{selected_genre.capitalize()} Vibes Playlist"
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)

    st.success(f"✅ Playlist '{playlist_name}' created!")
    st.write(f"👉 [Open in Spotify]({playlist['external_urls']['spotify']})")

# ---------------------------
# 📊 Fetch & Display User's Top Tracks (Optional)
# ---------------------------
if st.button("Show My Top Tracks"):
    top_tracks = sp.current_user_top_tracks(limit=10, time_range='medium_term')

    for idx, track in enumerate(top_tracks['items']):
        st.write(f"{idx+1}. {track['name']} by {track['artists'][0]['name']}")
