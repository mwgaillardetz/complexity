from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from dotenv import load_dotenv
import subprocess

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")  # For flash messages

# Load environment variables from .env file
load_dotenv()

def load_settings():
    return {
        'PLEX_URL': os.getenv('PLEX_URL'),
        'PLEX_TOKEN': os.getenv('PLEX_TOKEN'),
        'PLEX_LIBRARY_SECTION_ID': os.getenv('PLEX_LIBRARY_SECTION_ID'),
        'client_id': os.getenv('client_id'),
        'client_secret': os.getenv('client_secret'),
        'playlist_ids': os.getenv('playlist_ids')
    }

@app.route('/settings', methods=['GET', 'POST'])
def load_settings():
    return {
        'PLEX_URL': os.getenv('PLEX_URL'),
        'PLEX_TOKEN': os.getenv('PLEX_TOKEN'),
        'PLEX_LIBRARY_SECTION_ID': os.getenv('PLEX_LIBRARY_SECTION_ID'),
        'client_id': os.getenv('client_id'),
        'client_secret': os.getenv('client_secret'),
        'playlist_ids': os.getenv('playlist_ids')
    }

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Get the playlist_ids from the form and split it by commas
        playlist_ids = request.form['playlist_ids'].strip()
        if playlist_ids:
            playlist_ids_list = playlist_ids.split(',')
        else:
            playlist_ids_list = []

        # Update settings in .env file
        with open('.env', 'w') as f:
            f.write(f"FLASK_APP=app.py\n")
            f.write(f"FLASK_ENV=development\n")
            f.write(f"PLEX_URL='{request.form['PLEX_URL']}'\n")
            f.write(f"PLEX_TOKEN='{request.form['PLEX_TOKEN']}'\n")
            f.write(f"PLEX_LIBRARY_SECTION_ID='{request.form['PLEX_LIBRARY_SECTION_ID']}'\n")
            f.write(f"client_id='{request.form['client_id']}'\n")
            f.write(f"client_secret='{request.form['client_secret']}'\n")
            # Join the playlist IDs list back into a single string with commas
            f.write(f"playlist_ids='{','.join(playlist_ids_list)}'\n")

        # Reload environment variables and manually update os.environ
        load_dotenv()  # This loads the updated .env file
        os.environ["PLEX_URL"] = request.form["PLEX_URL"]
        os.environ["PLEX_TOKEN"] = request.form["PLEX_TOKEN"]
        os.environ["PLEX_LIBRARY_SECTION_ID"] = request.form["PLEX_LIBRARY_SECTION_ID"]
        os.environ["client_id"] = request.form["client_id"]
        os.environ["client_secret"] = request.form["client_secret"]
        os.environ["playlist_ids"] = ','.join(playlist_ids_list)

        flash("Settings updated successfully!", "success")
        return redirect(url_for("settings"))

    # Load updated settings (from os.environ)
    settings_data = load_settings()
    
    return render_template("settings.html", settings=settings_data)

@app.route('/playlists')
def playlists():
    return render_template('playlists.html', title="Playlists")

@app.route('/')
def home():
    return render_template('home.html', title="Home")

# Logic for button/playlist sync
@app.route('/sync-playlists')
def sync_playlists():
    subprocess.run(['python', 'program/sync-playlists.py'])
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5020, debug=True)
