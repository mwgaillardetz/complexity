from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from celery import Celery
import os
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")  # For flash messages

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # Redis as broker
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'  # Redis to store results

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task(bind=True)
def run_python_script(self):
    try:
        # Replace this with the actual path to your script
        subprocess.run(['python', 'path_to_your_script.py'], check=True)
        return {'status': 'success', 'message': 'Script executed successfully!'}
    except subprocess.CalledProcessError as e:
        raise self.retry(exc=e)

@app.route('/run_script', methods=['POST'])
def run_script():
    task = run_python_script.apply_async()  # Run the task asynchronously
    return jsonify({'status': 'started', 'task_id': task.id})

@app.route('/task_status/<task_id>')
def task_status(task_id):
    task = run_python_script.AsyncResult(task_id)
    if task.state == 'PENDING':
        return jsonify({'status': 'Task is still pending...'})
    elif task.state == 'SUCCESS':
        return jsonify({'status': 'success', 'message': task.result['message']})
    elif task.state == 'FAILURE':
        return jsonify({'status': 'error', 'message': str(task.result)})

# Function to update the .env file without overwriting
def update_env_file():
    try:
        # Load existing variables
        env_vars = {}
        if os.path.exists(".env"):
            with open(".env", "r") as env_file:
                for line in env_file:
                    key, _, value = line.partition("=")
                    env_vars[key.strip()] = value.strip()

        # Update with current environment
        updated_vars = {
            "PLEX_URL": os.environ.get("PLEX_URL", ""),
            "PLEX_TOKEN": os.environ.get("PLEX_TOKEN", ""),
            "PLEX_LIBRARY_SECTION_ID": os.environ.get("PLEX_LIBRARY_SECTION_ID", ""),
            "client_id": os.environ.get("client_id", ""),
            "client_secret": os.environ.get("client_secret", ""),
            "playlist_ids": os.environ.get("playlist_ids", ""),
        }

        # Merge and write back to .env
        env_vars.update(updated_vars)
        with open(".env", "w") as env_file:
            for key, value in env_vars.items():
                env_file.write(f"{key}={value}\n")
    except IOError as e:
        flash(f"Error saving settings: {str(e)}", "danger")

# Helper function to load settings
def load_settings():
    return {
        "PLEX_URL": os.getenv("PLEX_URL", ""),
        "PLEX_TOKEN": os.getenv("PLEX_TOKEN", ""),
        "PLEX_LIBRARY_SECTION_ID": os.getenv("PLEX_LIBRARY_SECTION_ID", ""),
        "client_id": os.getenv("client_id", ""),
        "client_secret": os.getenv("client_secret", ""),
        "playlist_ids": os.getenv("playlist_ids", "").split(","),
    }

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # Update environment variables
        for key in load_settings():
            os.environ[key.upper()] = request.form.get(key.lower(), "")

        # Update the .env file
        update_env_file()
        flash("Settings updated successfully!", "success")
        return redirect(url_for("settings"))

    return render_template("settings.html", settings=load_settings())

@app.route('/playlists')
def playlists():
    return render_template('playlists.html', title="Playlists")

@app.route('/')
def home():
    return render_template('home.html', title="Home")

# Define the main route of the web application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020, debug=True)
