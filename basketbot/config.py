import os

class Config(object):
    CONFIG_NAME = "base"
    TESTING = False
    STATIC_FOLDER = os.path.realpath(os.path.join(__file__, "../static"))
    # REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'

class Production(Config):
    CONFIG_NAME="production"

class Testing(Config):
    TESTING = True
    CONFIG_NAME = "testing"
