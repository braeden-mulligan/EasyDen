export FLASK_APP=server_main.py
export FLASK_ENV=development
export FLASK_DEBUG=1

#python3 server_main.py &

flask run --host=0.0.0.0 --port=80

unset FLASK_DEBUG
unset FLASK_ENV
unset FLASK_APP
