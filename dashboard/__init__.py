from flask import Flask

dashboard_app = Flask(__name__)

from . import routes
