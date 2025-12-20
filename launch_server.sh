#!/bin/bash

if [[ $1 == dev ]]; then 
	cd /home/braeden/Projects/EasyDen
else
	cd /home/braeden/EasyDen
fi

cd voice-command
# python3 speech_recognition.py &

cd ../server/dashboard-frontend
nohup npm install > /dev/null 2>&1 &
nohup npm run build > /dev/null 2>&1 &

cd ../database
nohup ./db_init.sh > /dev/null 2>&1 &

cd ..
nohup python3 device-manager-main.py > /dev/null 2>&1 &

if [[ $1 == dev ]]; then
	nohup python3 ./dashboard-main.py > /dev/null 2>&1 &
else
	nohup gunicorn -b localhost:8000 -w 2 dashboard-main:dashboard_app > /dev/null 2>&1 &
fi


