# Use an official Python runtime
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the app and dependencies
COPY . /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip ffmpeg git && \
    python3 -m pip install --user pipx && \
    python3 -m pipx ensurepath && \
    pipx install https://get.zotify.xyz

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask's port
EXPOSE 5020

# Run the app
CMD ["python", "app.py"]
