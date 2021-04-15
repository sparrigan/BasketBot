"""
Handles API endpoints relating to DOM elements stored in basketbot DB
"""

from flask import jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_cors import cross_origin
from basketbot import db
from basketbot.api import api
from basketbot.datamodel import model as dm
from basketbot.schemas import DOMName

blp_dom_elem = Blueprint("dom_elem", "dom_elem", url_prefix="/api/v1/")

@blp_dom_elem.route('/dom_elem')
class DOMElem(MethodView):
    @blp_dom_elem.arguments(DOMName, location='json')
    @blp_dom_elem.response(200, dm.DOMElem.Schema())
    def post(self, data):
        dom_elem = dm.DOMElem.query.filter(dm.DOMElem.js_name==data.get('js_name')).first()
        if dom_elem is not None:
            return dom_elem
        else:
            abort(404)
        


