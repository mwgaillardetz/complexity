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
        with open(".env", "r") as env_file:
            lines = env_file.readlines()

        updated_vars = {
            "FIELD1": os.environ["FIELD1"],
            "FIELD2": os.environ["FIELD2"],
            "FIELD3": os.environ["FIELD3"],
            "FIELD4": os.environ["FIELD4"],
            "FIELD5": os.environ["FIELD5"],
        }

        with open(".env", "w") as env_file:
            for line in lines:
                for key, value in updated_vars.items():
                    if line.startswith(f"{key}="):
                        line = f"{key}={value}\n"
                        break
                env_file.write(line)

            for key, value in updated_vars.items():
                if not any(line.startswith(f"{key}=") for line in lines):
                    env_file.write(f"{key}={value}\n")
    except IOError as e:
        flash(f"Error saving settings: {str(e)}", "danger")
        return redirect(url_for("settings"))

# Route for the settings page
@app.route("/settings", methods=["GET", "POST"])
def index():
    return render_template("index.html")
def settings():
    if request.method == "POST":
        # Update environment variables
        os.environ["FIELD1"] = request.form.get("field1", "")
        os.environ["FIELD2"] = request.form.get("field2", "")
        os.environ["FIELD3"] = request.form.get("field3", "")
        os.environ["FIELD4"] = request.form.get("field4", "")
        os.environ["FIELD5"] = request.form.get("field5", "")

        # Update the .env file
        update_env_file()

        flash("Settings updated successfully!", "success")
        return redirect(url_for("settings"))

    # Load current settings
    settings = {
        "field1": os.getenv("FIELD1", ""),
        "field2": os.getenv("FIELD2", ""),
        "field3": os.getenv("FIELD3", ""),
        "field4": os.getenv("FIELD4", ""),
        "field5": os.getenv("FIELD5", ""),
    }
    return render_template("settings.html", settings=settings)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020)
