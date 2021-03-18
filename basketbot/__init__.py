import os, uuid
from pathlib import Path
from flask import Flask
from .database import db, migrate

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
    db_path = os.path.join(Path(os.path.dirname(__file__)).parent, 'flasksip.db')
    db_string = 'sqlite:///{}'.format(db_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_string 

def create_app(config="flasksip.config.Testing"):
    """ Build out app and configure """
    app = Flask(__name__)
    configure(app, config)
    db.init_app(app)
    migrate.init_app(app, db)
    # app.register_blueprint(frontend)
    # app.register_blueprint(api, url_prefix="/api/v1")
    # app.redis = Redis.from_url(app.config['REDIS_URL'])
    # app.my_queue_name_here = rq.Queue('my_queue_name', connection=app.redis)
    return app




