FROM python:3.11-slim

# pyaudio requires portaudio; aplay (for audio feedback tones) is in alsa-utils
RUN apt-get update && apt-get install -y --no-install-recommends \
        portaudio19-dev \
        alsa-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY common/ common/
COPY files/ files/
COPY voice-command/ voice-command/

# Use the Docker-specific config (sets root path to /app)
COPY files/json/config.docker.json files/json/config.json

RUN pip install --no-cache-dir \
    vosk \
    pyaudio \
    requests

# Vosk downloads its language model (~50 MB) on first run into ~/.cache/vosk.
# Mount a volume at /root/.cache/vosk to persist it across container restarts:
#   docker volume create vosk_model
#   (add to compose voice-command volumes: vosk_model:/root/.cache/vosk)
VOLUME ["/root/.cache/vosk"]

WORKDIR /app/voice-command

CMD ["python3", "speech_recognition.py"]
