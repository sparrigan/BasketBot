import os
from pathlib import Path

class Config(object):
    CONFIG_NAME = "base"
    TESTING = False
    STATIC_FOLDER = os.path.realpath(os.path.join(__file__, "../static"))
    # REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'

class Production(Config):
    CONFIG_NAME="production"
    # Temporarily use SQLITE for dev
    db_path = os.path.join(Path(os.path.dirname(__file__)).parent, 'basketbot.db')
    db_string = 'sqlite:///{}'.format(db_path)
    SQLALCHEMY_DATABASE_URI = db_string 


class Testing(Config):
    TESTING = True
    CONFIG_NAME = "testing"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_USER = "nic"
    DB_NAME = "test"
    DB_VERSION = 13.2
    
    fmtstring = "postgres://{}@{}:{}/{}"
    db_string = fmtstring.format(DB_USER, DB_HOST, DB_PORT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = db_string 


