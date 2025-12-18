FROM python:3.11-slim

# Install system dependencies for Tkinter and X11
RUN apt-get update && apt-get install -y \
    python3-tk \
    xvfb \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY .  .

# Set display environment variable for virtual display
ENV DISPLAY=:99

# Run with Xvfb (virtual display server)
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x16 & python run.py"]