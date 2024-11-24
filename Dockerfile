# Use an official Python runtime
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the app and dependencies
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask's port
EXPOSE 5020

# Run the app
CMD ["python", "app.py"]
