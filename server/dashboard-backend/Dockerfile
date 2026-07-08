FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    nodejs \
    npm \
	curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/

COPY common/ common/
COPY device-firmware/libraries/common/ device-firmware/libraries/common/
COPY files/ files/
COPY server/ server/

RUN cd /app/server/dashboard-frontend && npm install && npm run build

RUN pip install --no-cache-dir \
    flask \
    flask-cors \
    flask-bcrypt \
    flask-jwt-extended \
    requests \
    gunicorn

WORKDIR /app/server

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:7000", "-w", "2", "dashboard-main:dashboard_app"]