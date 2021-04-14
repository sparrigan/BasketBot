"""
Handles API endpoints relating to browser extensions
"""

from flask import jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_cors import cross_origin
from basketbot import db
from basketbot.api import api
from basketbot.datamodel import model as dm
from basketbot.schemas import SiteURL, ExtensionScrapingRule, IDArgs, FormRegion, CountryRegions, CountryRegionsDict, DeconstructedURL, RetailSiteRegionIDs
from basketbot.util import decompose_url
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

@blp.route('/retailsite')
class RetailSite(MethodView):
    @blp.arguments(RetailSiteRegionIDs, location='json')
    @blp.response(200, dm.RetailSite.Schema())
    def post(self, data):
        pass


@blp.route('/checksite')
class CheckSite(MethodView):
    @blp.arguments(SiteURL, location='json')
    @blp.response(200, dm.RetailSite.Schema())
    def post(self, data):
        url = data['url']
        site = dm.RetailSite.get_site_from_url(url)
        if site is None:
            abort(404, 'No retail site associated with URL found in BasketBot')
        # elif len(site)>1:
            # abort(500, 'Multiple retail sites found in BasketBot associated with URL')
        else:
            return site

@blp.route('/deconstructurl')
class DeconstructURL(MethodView):
    @blp.arguments(SiteURL, location='json')
    @blp.response(200, DeconstructedURL())
    def post(self, data):
        url = data['url']
        return decompose_url(url)
 

@blp.route('/country')
class Country(MethodView):
    @blp.response(200, CountryRegions(many=True))
    def get(self):
        return dm.Country.query.all()

@blp.route('/countryregionsdict')
class CountryRegionsDict(MethodView):
    # @blp.response(200, CountryRegionsDict(many=True))
    def get(self):
         countries = CountryRegions(many=True).dump(dm.Country.query.all())
         return {country.pop('name'): country for country in countries}

@blp.route('/region')
class Region(MethodView):
    @blp.response(200, FormRegion(many=True))
    def get(self):
        return dm.Region.query.all()

# TODO: Add user validation through oauth
@blp.route('/scrapingrule', methods=['GET', 'POST', 'OPTIONS'])
class ScrapingRule(MethodView):
    @blp.arguments(IDArgs, location='query')
    @blp.response(200, dm.ScrapingRule.Schema())
    def get(self, args):
        """
        Get a scraping rule by ID
        """
        return dm.ScrapingRule.query.get(args.get('id'))

    @blp.arguments(ExtensionScrapingRule, location='json')
    @blp.response(200, dm.ScrapingRule.Schema())
    def post(self, data):
        db.session.add(data)
        db.session.commit()
        return data
