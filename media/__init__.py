""" Flask App"""
from flask import Flask
from credentials.credentials_info import SESSION_SECRET_KEY
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Create App Object
app = Flask(__name__)
# Gets the base directory for the current file
base_dir = os.path.abspath(os.path.dirname(__file__))

# Configuring session
app.config['SESSION_COOKIE_NAME'] = "Ansh's Session"
app.secret_key = SESSION_SECRET_KEY

# Configuring Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, "db.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Marshmallow
ma = Marshmallow(app)

# Initialize Database
db = SQLAlchemy(app)

from media import routes
