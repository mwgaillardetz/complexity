import logging
import os
import requests
import time
from plexapi.server import PlexServer
from plexapi.playlist import Playlist
from plexapi.exceptions import NotFound
from thefuzz import fuzz
from dotenv import load_dotenv
import subprocess
import datetime

load_dotenv()

# Plex server details
PLEX_URL = os.getenv('PLEX_URL')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
PLEX_LIBRARY_SECTION_ID = int(os.getenv('PLEX_LIBRARY_SECTION_ID'))
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
playlist_ids = os.getenv('PLAYLIST_IDS').split(',')

# Download above spotify playlists to W:\Music\{Artist}\{Album}\{Artist} - {Song}.{ext}
commands = [
    rf'zotify https://open.spotify.com/playlist/{playlist_id} --output "{{artist}}\{{album}}\{{artist}} - {{song_name}}.{{ext}}"'
    for playlist_id in playlist_ids
]
# Join the commands using ';' for sequential execution in PowerShell
joined_commands = ' ; '.join(commands)
# Run the joined commands in PowerShell
subprocess.run(['pwsh', '-Command', joined_commands], check=True)

def authenticate_spotify(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

def get_playlist_tracks(token, playlist_ids):
    all_tracks = []
    playlist_names = []
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    for playlist_id in playlist_ids:
        playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
        response = requests.get(playlist_url, headers=headers)
        playlist_data = response.json()
        if 'tracks' not in playlist_data:
            logging.error(f"'tracks' key not found in the response for playlist ID {playlist_id}. Response data: {playlist_data}")
            continue
        tracks = []
        next_url = playlist_data['tracks']['next']
        while next_url:
            for item in playlist_data['tracks']['items']:
                track = item['track']
                tracks.append(f"{track['name']} - {track['artists'][0]['name']}")
            response = requests.get(next_url, headers=headers)
            playlist_data['tracks'] = response.json()
            next_url = playlist_data['tracks']['next']
        # Add the last set of tracks after the loop exits
        for item in playlist_data['tracks']['items']:
            track = item['track']
            tracks.append(f"{track['name']} - {track['artists'][0]['name']}")
        all_tracks.append(tracks)
        playlist_names.append(playlist_data['name'])
    return all_tracks, playlist_names

def sync_playlist_with_plex(plex, playlist_name, spotify_tracks):
    # Fetch all tracks from the Plex server
    plex_tracks = plex.library.sectionByID(PLEX_LIBRARY_SECTION_ID).all()
    plex_tracks_flat = [track for artist in plex_tracks for album in artist.albums() for track in album.tracks()]

    # Match Spotify tracks to Plex tracks
    playlist_tracks = []
    unmatched_tracks = []

    for spotify_track in spotify_tracks:
        matched = False
        for plex_track in plex_tracks_flat:
            if fuzz.token_set_ratio(spotify_track, f"{plex_track.title} - {plex_track.grandparentTitle}") > 90:
                playlist_tracks.append(plex_track)
                matched = True
                break
        if not matched:
            unmatched_tracks.append(spotify_track)

    if playlist_tracks:
        # Create or update the playlist in Plex
        try:
            playlist = plex.playlist(playlist_name)
            playlist.removeItems(playlist.items())
        except NotFound:
            playlist = Playlist.create(plex, playlist_name, items=playlist_tracks)
        playlist.addItems(playlist_tracks)

        logging.info(f"Added {len(playlist_tracks)} tracks to playlist: {playlist_name}")
        logging.info(f"{len(unmatched_tracks)} tracks were not matched for playlist: {playlist_name}")
        return playlist
    else:
        logging.error(f"No matching tracks found for playlist: {playlist_name}")

# Main execution
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
logging.info(f"\n-----\nLog Start for {current_date}\n-----")
plex = PlexServer(PLEX_URL, PLEX_TOKEN)

# Re-scan music library in case new material has been added
try:
    music_library = plex.library.sectionByID(PLEX_LIBRARY_SECTION_ID)
    music_library.update()
    logging.info("Plex music library scan initiated.")
    logging.info("Pausing script for 15 minutes to allow the scan to complete.")
    time.sleep(15 * 60)  # Pause for 15 minutes
except NotFound:
    logging.error("Music library not found. Check your PLEX_LIBRARY_SECTION_ID.")
except Exception as e:
    logging.error(f"An error occurred while trying to scan the music library: {e}")

token = authenticate_spotify(client_id, client_secret)
all_tracks, playlist_names = get_playlist_tracks(token, playlist_ids)

# Sync each playlist with Plex
for i in range(len(playlist_names)):
    playlist_name = playlist_names[i]
    spotify_tracks = all_tracks[i]
    sync_playlist_with_plex(plex, playlist_name, spotify_tracks)



# -----------------------------------------------------------------------
# NOT NECESSARY - Add new tracks from 'local-addition' to '0Champloo' playlist
# Retrieve the 'local-addition' and '0Champloo' playlists
local_addition_playlist = None
champloo_playlist = None
for playlist in plex.playlists():
    if playlist.title == 'local-addition':
        local_addition_playlist = playlist
    elif playlist.title == '0Champloo':
        champloo_playlist = playlist

# If both playlists exist
if local_addition_playlist and champloo_playlist:
    # Get the tracks from both playlists
    local_addition_tracks = local_addition_playlist.items()
    champloo_tracks = champloo_playlist.items()

    # Tracks to be added to '0Champloo'
    tracks_to_add = []

    # Compare the tracks from 'local-addition' with the tracks in '0Champloo'
    for track in local_addition_tracks:
        if track not in champloo_tracks:
            # If a track from 'local-addition' is not in '0Champloo', add it to the list of tracks to add
            tracks_to_add.append(track)

    # If there are tracks to add
    if tracks_to_add:
        # Add the tracks to the '0Champloo' playlist
        champloo_playlist.addItems(tracks_to_add)

        logging.info(f"Added {len(tracks_to_add)} tracks from 'local-addition' to '0Champloo'")
    else:
        logging.info("No new tracks to add from 'local-addition' to '0Champloo'")
else:
    logging.error("'local-addition' or '0Champloo' playlist not found")