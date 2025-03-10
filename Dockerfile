FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libglew-dev \
    freeglut3-dev \
    mesa-utils \
    x11-xserver-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0

# Create a non-root user
RUN useradd -m dungeonuser
USER dungeonuser

# Set default command
ENTRYPOINT ["dungeon-descent"]
CMD ["2d"]  # Default to 2D mode

# Usage:
# To run in 2D mode: docker run --rm -it dungeon-descent
# To run in 3D mode: docker run --rm -it dungeon-descent 3d
# For 3D with X11 forwarding:
# docker run --rm -it -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix dungeon-descent 3d 