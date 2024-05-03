FROM python:3.11-slim

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /usr/src/app

# Copy requirements first to leverage Docker cache
# COPY requirements.txt ./

# Install necessary packages for FFmpeg and libmp3lame
RUN apt-get update && apt-get install -y \
    wget \
    nano \
    git \
    build-essential \
    yasm \
    pkg-config \
    libmp3lame-dev  # Added this line

# Clone and compile FFmpeg with libmp3lame support
RUN git clone --depth 1 --branch n4.4 https://github.com/FFmpeg/FFmpeg /root/ffmpeg && \
    cd /root/ffmpeg && \
    ./configure --enable-nonfree --enable-libmp3lame --disable-shared --extra-cflags=-I/usr/local/include && \
    make -j$(nproc) && make install && \
    cd / && rm -rf /root/ffmpeg

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* 

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt



# Copy the rest of the app
COPY --chown=appuser:appuser . .

USER appuser

# Ensure run.sh is executable
# RUN chmod +x run.sh

# EXPOSE 8000

# CMD ["./run.sh"]
EXPOSE 8000

# HEALTHCHECK CMD curl --fail http://localhost:8000/_stcore/health

ENTRYPOINT ["streamlit", "run", "A_Information.py", "--server.port=8000", "--server.address=0.0.0.0"]