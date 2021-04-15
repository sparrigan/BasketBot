from flask import Blueprint

frontend = Blueprint("frontend", __name__)

@frontend.route("/", methods=["GET"])
def index():
    return "hello"

from basketbot.frontend import retail_site
from basketbot.frontend import scraping

frontend.add_url_rule("/retail_site/create", methods=["GET", "POST"], endpoint="retail_site_create", view_func=retail_site.create)
# frontend.add_url_rule("/scraping_rule/create", methods=["GET", "POST"], endpoint="scraping_rule_create", view_func=scraping.create)
frontend.add_url_rule("/scraping_rule/get_form", methods=["GET", "POST"], endpoint="scraping_rule_get_form", view_func=scraping.get_form)
