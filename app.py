from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")  # For flash messages

# Route for the settings page
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # Update environment variables
        os.environ["FIELD1"] = request.form.get("field1", "")
        os.environ["FIELD2"] = request.form.get("field2", "")
        os.environ["FIELD3"] = request.form.get("field3", "")
        os.environ["FIELD4"] = request.form.get("field4", "")
        os.environ["FIELD5"] = request.form.get("field5", "")

        # Update the .env file
        with open(".env", "w") as env_file:
            env_file.write(f"FIELD1={os.environ['FIELD1']}\n")
            env_file.write(f"FIELD2={os.environ['FIELD2']}\n")
            env_file.write(f"FIELD3={os.environ['FIELD3']}\n")
            env_file.write(f"FIELD4={os.environ['FIELD4']}\n")
            env_file.write(f"FIELD5={os.environ['FIELD5']}\n")

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
    app.run(debug=True)
