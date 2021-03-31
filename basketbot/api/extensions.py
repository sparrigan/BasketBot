from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from basketbot.api import api
from basketbot.schemas import TestSchema
# from flask_restx import Resource, Namespace

# ns_ext = Namespace(
#         'extensions',
#         description='API endpoints for dealing with web browser extensions'
#         )

blp = Blueprint("api", "api", url_prefix="/api/v1/")

@blp.route('/test')
class Scrape(MethodView):
    # @blp.arguments(TestSchema, location='query')
    # @blp.response(200, TestSchema(many=True))
    def get(self):
        """
        Just a test
        """
        response = jsonify({"out": "working"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        from time import sleep
        sleep(10)
        return response

