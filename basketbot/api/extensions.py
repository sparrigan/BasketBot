"""
Handles API endpoints relating to browser extensions
"""

from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from basketbot.api import api
from basketbot.datamodel import model as dm
from basketbot.schemas import SiteURL
# from flask_restx import Resource, Namespace

# ns_ext = Namespace(
#         'extensions',
#         description='API endpoints for dealing with web browser extensions'
#         )

blp = Blueprint("api", "api", url_prefix="/api/v1/")

@blp.route('/ping')
class Ping(MethodView):
    def get(self):
        return "pong"

@blp.route('/checksite')
class CheckSite(MethodView):
    @blp.arguments(SiteURL)
    def post(self, data):
        url = data['base_url']
        dm.RetailSite

@blp.route('/scraperule')
class Scrape(MethodView):
    # @blp.arguments(TestSchema, location='query')
    # @blp.response(200, TestSchema(many=True))
    def get(self):

        """
        Just a test
        """
        # 1. Validation of input using marshmallow schema

        # 2. Then validate entries of class_chain JSON from DOMElem entries
        
        # 3. Create ScrapingRule entry

        # 4. Return 200

        # 5. Add user validation through oauth


        response = jsonify({"out": "working"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        from time import sleep
        sleep(10)
        return response

    # @blp.arguments(dm.ScrapingRule.Schema(exclude=["update_time", "id", "user_id"]))
    # def post(self):
    #     pass

