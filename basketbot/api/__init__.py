from flask_smorest import Api, Blueprint
import basketbot.datamodel.swagger as dm_swagger
from basketbot.datamodel.swagger import definitions

# Register a blueprint to contain the API endpoints
api = Api(
        spec_kwargs={
            "version": "0.1",
            "openapi_version": "3.0.0",
            "title":"BasketBotAPI",
            "description":"API for web extensions to talk with BasketBot"
            }
        )

from .extensions import blp
from .dom_elem import blp_dom_elem

# Register our swagger models. Model definitions are stored
# as a list of (Name, dict) tuples, where dicts are {field_name: type}
# Store resulting flask_restx model objects in a class
# class Models:
#     def __init__(self, ms):
#         self.__dict__.update(ms)
# models = Models({_[0]: api.model(_[0], _[1]) for _ in definitions})

# api.register_blueprint(blueprint)
