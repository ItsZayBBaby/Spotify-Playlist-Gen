import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify Credentials from Streamlit Secrets
SPOTIPY_CLIENT_ID = st.secrets["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = st.secrets["SPOTIPY_CLIENT_SECRET"]
# IMPORTANT: Use your actual deployed Streamlit app URL here
SPOTIPY_REDIRECT_URI = "https://your-app-name.streamlit.app"  

# Initialize OAuth with manual login (no caching to avoid reusing your token)
auth_manager = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-top-read playlist-modify-public playlist-modify-private",
    show_dialog=True,
    cache_path=None  # Do not cache the token, so each user must log in
)

# Initialize Spotify client variable
sp = None

st.title("🎵 Genre-Based Playlist Generator")

# Use st.query_params to retrieve query parameters from the URL
query_params = st.query_params
auth_code = query_params.get("code", None)

if auth_code:
    # If auth_code is present, try to exchange it for an access token
    try:
        token_info = auth_manager.get_access_token(auth_code, as_dict=True)
        if not token_info or "access_token" not in token_info:
            st.error("Failed to obtain access token. Please try re-authenticating.")
            st.stop()
        # Debug: Show token info length (for development only; remove in production)
        st.write("Token obtained successfully. (Length:", len(token_info["access_token"]), ")")
        st.session_state.spotify_token = token_info["access_token"]
    except Exception as e:
        st.error(f"Error during token retrieval: {e}")
        st.stop()
else:
    # No auth code in query params, so prompt the user to log in.
    auth_url = auth_manager.get_authorize_url()
    st.markdown(f"[Click here to authorize Spotify]({auth_url})")
    st.stop()  # Halt execution until user logs in

# Once token is set, create the Spotify client
if "spotify_token" in st.session_state:
    sp = spotipy.Spotify(auth=st.session_state.spotify_token)
    st.success("✅ Authentication successful! You can now generate playlists.")
else:
    st.error("No Spotify token found. Please log in.")
    st.stop()

# Fetch valid genres from Spotify to ensure the seed is valid.
try:
    valid_genres = sp.recommendation_genre_seeds()["genres"]
except Exception as e:
    st.error(f"⚠️ Error fetching valid genres: {e}")
    st.stop()

# Allow user to select one of the valid genres
selected_genre = st.selectbox("Select a Genre:", valid_genres)

if st.button("Generate Playlist"):
    if selected_genre not in valid_genres:
        st.error(f"⚠️ '{selected_genre}' is not a valid genre for recommendations.")
        st.stop()

    try:
        recommendations = sp.recommendations(seed_genres=[selected_genre], limit=20)
        track_uris = [track["uri"] for track in recommendations["tracks"]]
    except Exception as e:
        st.error(f"⚠️ Error fetching recommendations: {e}")
        st.stop()

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

