export FLASK_APP=main.py
export FLASK_ENV=development
export FLASK_DEBUG=1

cd voice-command
python3 speech_recognition.py &

cd ../server/dashboard-frontend
npm run build

cd ../database
./db_init.sh

cd ..
python3 device-manager-main.py &

flask run --host=0.0.0.0 --port=80

unset FLASK_DEBUG
unset FLASK_ENV
unset FLASK_APP
