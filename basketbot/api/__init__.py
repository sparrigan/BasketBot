from flask import Blueprint
from flask_restx import Api
import basketbot.datamodel.swagger as dm_swagger
from basketbot.datamodel.swagger import definitions

# Register a blueprint to contain the API endpoints
blueprint = Blueprint("api", "api")
api = Api(
        blueprint,
        version="0.1",
        title="BasketBotAPI",
        description="API for web extensions to talk with BasketBot"
        )
# Register our swagger models. Model definitions are stored
# as a list of (Name, dict) tuples, where dicts are {field_name: type}
# Store resulting flask_restx model objects in a class
class Models:
    def __init__(self, ms):
        self.__dict__.update(ms)
models = Models({_[0]: api.model(_[0], _[1]) for _ in definitions})

from .extensions import ns_ext

api.add_namespace(ns_ext)
