export FLASK_APP=dashboard/__init__.py
export FLASK_ENV=development
export FLASK_DEBUG=1

flask run --host=0.0.0.0 --port=80

unset FLASK_DEBUG
unset FLASK_ENV
unset FLASK_APP
