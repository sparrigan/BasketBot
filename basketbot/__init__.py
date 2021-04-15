import os, uuid
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from .exceptions import *
from .database import db, migrate
from basketbot.datamodel import register_events
from .marshalling import ma
from basketbot.frontend import frontend
from basketbot.api import api
from basketbot.api import blp, blp_dom_elem

if "XDG_CONFIG_HOME" in os.environ:
    HOME = os.getenv("XDG_CONFIG_HOME")
    HOME_CONFIG = os.path.join(HOME, "basketbot", "basketbot.cfg")
else:
    HOME = os.path.expanduser("~")
    HOME_CONFIG = os.path.join(HOME, ".config", "basketbot", "basketbot.cfg")

def configure(app, config):
    """ Configure Flask app """
    app.secret_key = str(uuid.uuid4())
    app.config.from_object(config)

    if os.path.exists(HOME_CONFIG):
        app.config.from_pyfile(HOME_CONFIG)
    if "STATIC_FOLDER" in app.config:
        app.static_folder = app.config["STATIC_FOLDER"]
    if "TEMPLATE_FOLDER" in app.config:
        app.template_folder = app.config["TEMPLATE_FOLDER"]

    # Manually override SQLA DB URI for sqlite 
    # db_path = os.path.join(Path(os.path.dirname(__file__)).parent, 'basketbot.db')
    # db_string = 'sqlite:///{}'.format(db_path)
    # app.config['SQLALCHEMY_DATABASE_URI'] = db_string 

def create_app(config="basketbot.config.Testing"):
    """ Build out app and configure """

    app = Flask(__name__)
    configure(app, config)
    # Enable CORS for all api endpoints from browser extensions
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    # Register any db event listeners
    register_events(db.session) 
    migrate.init_app(app, db)
    ma.init_app(app) # Note: important this comes after db.init_app
    api.init_app(app)
    # app.register_blueprint(frontend)
    app.register_blueprint(frontend)
    api.register_blueprint(blp)
    api.register_blueprint(blp_dom_elem)
    # app.redis = Redis.from_url(app.config['REDIS_URL'])
    # app.my_queue_name_here = rq.Queue('my_queue_name', connection=app.redis)

    return app
