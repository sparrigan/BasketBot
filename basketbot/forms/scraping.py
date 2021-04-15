from flask_wtf import FlaskForm
from wtforms import Form, fields
from wtforms_alchemy import QuerySelectMultipleField, QuerySelectField
from basketbot.datamodel import model as dm 

def get_retail_site():
    """ Populate retail site multiple select """
    return dm.RetailSite.query.order_by(dm.RetailSite.name.asc())

def get_retail_site_label(retail_site):
    """ Populate label for retail sites """
    return f'{retail_site.name} ({retail_site.get_site_url()})'

def get_default_retail_site():
    """ Return the alphabetically first retail site as default """
    return [get_retail_site().first()]

def get_dom_elem():
    """ Populate parent elem multiple select of DOM values """
    return dm.DOMElem.query.order_by(dm.DOMElem.bs_name.asc())

def get_default_dom_elem():
    """ Return the alphabetically first dom elem as parent elem default """
    return [get_dom_elem().first()]

class ScrapingRuleForm(FlaskForm):
    retail_site = QuerySelectMultipleField('Retail Site', query_factory=get_retail_site, get_label=get_retail_site_label, default=get_default_retail_site)
    parent_elem = QuerySelectField('Parent element type', query_factory=get_dom_elem, get_label='bs_name', default=get_default_dom_elem)
    parent_id = fields.StringField('Parent ID')
    class_chain = fields.TextAreaField('Class Chain', render_kw={'rows': 10})
    default_rule = fields.BooleanField('Use as default rule for this site', default=True)

