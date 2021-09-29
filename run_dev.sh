export FLASK_APP=app_top_level.py
export FLASK_ENV=development
export FLASK_DEBUG=1

flask run --host=0.0.0.0 --port=80

unset FLASK_DEBUG
unset FLASK_ENV
unset FLASK_APP
