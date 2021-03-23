from basketbot.api import api, models
from flask_restx import Resource, Namespace

ns_ext = Namespace(
        'extensions',
        description='API endpoints for dealing with web browser extensions'
        )

@ns_ext.route('')
class Scrape(Resource):
    def post(self):
        pass

