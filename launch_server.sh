export FLASK_APP=dashboard-main.py
export FLASK_ENV=development
export FLASK_DEBUG=1

cd /home/braeden/EasyDen

cd voice-command
# python3 speech_recognition.py &

cd ../server/dashboard-frontend
nohup npm install > /dev/null 2>&1 &
nohup npm run build > /dev/null 2>&1 &

cd ../database
nohup ./db_init.sh > /dev/null 2>&1 &

cd ..
nohup python3 device-manager-main.py > /dev/null 2>&1 &

nohup flask run --host=0.0.0.0 --port=80 > /dev/null 2>&1 &

unset FLASK_DEBUG
unset FLASK_ENV
unset FLASK_APP

