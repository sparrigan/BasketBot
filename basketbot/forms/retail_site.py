from flask_wtf import FlaskForm
from wtforms import Form, fields
from wtforms_alchemy import QuerySelectMultipleField
from basketbot.datamodel import model as dm 

def get_countries():
    """ Populate country multiple select """
    return dm.Country.query.order_by(dm.Country.name.asc())

def get_default_country():
    """ Return the alphabetically first country as default """
    return [get_countries().first()]

def get_regions():
    """ Begin by setting regions to those associated with the default country """
    country = get_default_country()[0]
    return dm.Region.query.filter(dm.Region.country==country)

class RetailSiteForm(FlaskForm):
    title = "Create a retail site in basketbot"
    short_title = "Create site"
    name = fields.StringField('Site Name')
    countries = QuerySelectMultipleField('Countries', query_factory=get_countries, get_label="name", default=get_default_country)
    regions = QuerySelectMultipleField('Regions', query_factory=get_regions, get_label="name")
    url_protocol = fields.StringField('Protocol')
    url_subdomain = fields.StringField('Subdomain')
    url_domain = fields.StringField('Domain')
    url_suffix = fields.StringField('Suffix')
    scraping_rule = fields.HiddenField('scraping_rule', render_kw={'id': 'scraping-rule-hidden'})
