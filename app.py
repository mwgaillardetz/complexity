from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")  # For flash messages

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
            "FIELD1": os.environ.get("FIELD1", ""),
            "FIELD2": os.environ.get("FIELD2", ""),
            "FIELD3": os.environ.get("FIELD3", ""),
            "FIELD4": os.environ.get("FIELD4", ""),
            "FIELD5": os.environ.get("FIELD5", ""),
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
        "field1": os.getenv("FIELD1", ""),
        "field2": os.getenv("FIELD2", ""),
        "field3": os.getenv("FIELD3", ""),
        "field4": os.getenv("FIELD4", ""),
        "field5": os.getenv("FIELD5", ""),
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
