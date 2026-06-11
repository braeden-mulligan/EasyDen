FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/

COPY common/ common/
COPY device-firmware/libraries/common/ device-firmware/libraries/common/
COPY files/ files/
COPY server/ server/

RUN pip install --no-cache-dir \
    schedule

WORKDIR /app/server

EXPOSE 1338
EXPOSE 8888

CMD ["python3", "device-manager-main.py"]