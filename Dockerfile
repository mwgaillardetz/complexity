# Use an official Python runtime
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the app and dependencies
COPY . /app

# Install system dependencies and pipx
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    python3 -m pip install pipx && \
    python3 -m pipx ensurepath && \
    export PATH=/root/.local/bin:$PATH && \
    pipx install https://get.zotify.xyz

# Add pipx to PATH for subsequent commands
ENV PATH=/root/.local/bin:$PATH

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask's port
EXPOSE 5020

# Run the app
CMD ["python", "app.py"]
