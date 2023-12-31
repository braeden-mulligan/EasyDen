import os, sys

sys.path.append(os.path.dirname(__file__))
 
from flask import Flask

dashboard_app = Flask(__name__)

import routes
