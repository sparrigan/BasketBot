"""
Handles API endpoints relating to browser extensions
"""

from flask import jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_cors import cross_origin
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
    # @cross_origin()
    @blp.arguments(SiteURL, location='json')
    @blp.response(200, dm.RetailSite.Schema())
    def post(self, data):
        url = data['url']
        site = dm.RetailSite.check_site_url(url)
        if len(site)==0:
            abort(404, 'No retail site associated with URL found in BasketBot')
        elif len(site)>1:
            abort(500, 'Multiple retail sites found in BasketBot associated with URL')
        else:
            return site[0]

@blp.route('/scraperule', methods=['GET', 'OPTIONS'])
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
        # response.headers.add('Access-Control-Allow-Origin', '*')
        # response.headers.add("Access-Control-Allow-Credentials", "true")
        # response.headers.add("Access-Control-Allow-Methods", "OPTIONS, GET, POST")
        # response.headers.add("Access-Control-Allow-Headers", "Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control")
        # from time import sleep
        # sleep(1)
        return response

    # @blp.arguments(dm.ScrapingRule.Schema(exclude=["update_time", "id", "user_id"]))
    # def post(self):
    #     pass

