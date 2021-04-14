from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import Schema, fields, ValidationError, validates_schema
from marshmallow.validate import Range
import requests
from basketbot import ma
from basketbot.datamodel import model as dm
from basketbot import InvalidDOMElem, InvalidClassChain, InvalidRetailSiteURL, InvalidURL

# Validators

def validate_dom_elem(check, js=False):
    """
    Short Summary
    -------------
    Check that a dom element string is contained in a bs_name value in the DB
    
    Parameters
    ----------
    check : str
        The string to check for containment in DB
    js : bool
        Whether the dom string is javascript formated (checked against js_name column
        in DOMElem relation). Otherwise checks against bs_name column which uses 
        BeautifulSoup formatting. Default - False
    """
    if js:
        known_elems = [x[0] for x in dm.DOMElem.query.with_entities(dm.DOMElem.js_name)]
    else:
        known_elems = [x[0] for x in dm.DOMElem.query.with_entities(dm.DOMElem.bs_name)]
    if check not in known_elems:
        raise InvalidDOMElem(f"Provided Parent element does not match any {'JavaScript' if js else 'BeautifulSoup'} element tag listed in basketbot DB")

def validate_class_chain(check):
    """
    Short Summary
    -------------
    Check that a class chain object contains correct structure and valid DOM elements
    """
    if not isinstance(check, dict):
        raise InvalidClassChain("ClassChain is not an object")
    cce = ClassChainElem()
    keys = check.keys()
    check_keys = [x.isnumeric() for x in keys]
    if not all(check_keys):
        raise InvalidClassChain("Provided ClassChain does not use numeric keys")
    if sorted(keys) != list(map(str, range(len(keys)))):
        raise InvalidClassChain("Provided ClassChain does not contain incremented 0-based labels")
    check_values = [cce.validate(val) for val in check.values()]
    if sum(len(x) for x in check_values)>0:
        raise InvalidClassChain(f"Failed to validate ClassChain contents with following errors: {check_values}")

# Schemas

class IDArgs(ma.Schema):
    """ Simple Schema for integer ID arguments """
    id = fields.Integer(validate=Range(min=1, max=None))

class NodeElem(ma.Schema):
    dom_type = fields.Str(validate=lambda x: validate_dom_elem(x,js=True))
    classes = fields.List(fields.Str())

class ClassChainElem(ma.Schema):
    tree_node = fields.Nested(NodeElem)
    siblings = fields.List(fields.Nested(NodeElem))

class ExtensionScrapingRule(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = dm.ScrapingRule
        load_instance = True
        include_relationships = False
        exclude = ("id", "update_time", "user_id") # Add back user eventually

    # Override some fields
    class_chain = fields.Raw(validate=validate_class_chain)
    items = fields.List(fields.Str()) # Update this properly when allowing items - may be able to use autogenerated relationship from ORM class
    # parent_elem_id = fields.Function(
    #         serialize=lambda obj: dm.DOMElem.query.get(obj.parent_elem_id).js_name,
    #         deserialize=lambda obj: dm.DOMElem.query.filter(dm.DOMElem.js_name==obj).scalar().id,
    #         # validate=validate_dom_elem_js, # This validates against BS rules
    #         data_key="parent_elem"
    #         )
    parent_elem_id = fields.Method(
            serialize="serialize_parent_elem",
            deserialize="deserialize_parent_elem",
            # validate=validate_dom_elem_js, # This validates against BS rules
            data_key="parent_elem"
            )
    retail_site_id = fields.Method(
            serialize="serialize_retail_site",
            deserialize="deserialize_retail_site",
            data_key="retail_site" # Need to confirm that this is the serialized key
            )

    def serialize_retail_site(self, obj):
        return obj.retail_site.get_site_url()

    def deserialize_retail_site(self, obj):
        if not isinstance(obj, str):
            raise InvalidRetailSiteURL('Retail Site URL must be a string')
        retail_site = dm.RetailSite.get_site_from_url(obj)
        if retail_site is not None:
            return retail_site.id
        else:
            raise InvalidRetailSiteURL()

    def serialize_parent_elem(self, obj):
        dom_elem = dm.DOMElem.query.get(obj.parent_elem_id)
        if dom_elem is not None:
            return dom_elem.js_name
        else:
            raise InvalidDOMElem('DOM element not found from ID')

    def deserialize_parent_elem(self, obj):
        dom_elem = dm.DOMElem.query.filter(dm.DOMElem.js_name==obj).scalar()
        if dom_elem is not None:
            return dom_elem.id
        else:
            raise InvalidDOMElem('DOM element not found from JavaScript tag name')

class FormRegion(ma.SQLAlchemySchema):
    class Meta:
        model = dm.Region
        load_instance = True
        include_relationships = True
    id = ma.auto_field(data_key="region_id")
    name = ma.auto_field() 

class CountryRegions(ma.SQLAlchemySchema):
    class Meta:
        model = dm.Country
        load_instance = True
        include_relationships = True
    id = ma.auto_field(data_key="country_id")
    name = ma.auto_field() 
    regions = fields.Nested(FormRegion, many=True)

class CountryRegionsDict(ma.SQLAlchemySchema):
    class Meta:
        model = dm.Country
        load_instance = True
        include_relationships = True
    id = ma.auto_field(data_key="country_id")
    name = ma.auto_field() 
    regions = fields.Nested(FormRegion, many=True)

class SiteURL(ma.Schema):
    url = ma.Str()

class DeconstructedURL(ma.Schema):
    subdomain = ma.Str()
    domain = ma.Str()
    suffix = ma.Str()
    protocol = ma.Str()

    @validates_schema
    def validate_url(self, data, **kwargs):
        url = f"{data.get('protocol')+'://' if data.get('protocol') else ''}"\
        f"{data.get('subdomain')+'.' if data.get('subdomain') else ''}"\
        f"{data.get('domain')}."\
        f"{data.get('suffix')}"
        try:
            response = requests.head(url)
        except requests.exceptions.ConnectionError:
            return False
        if not response.ok:
            return False
        return True


class RetailSiteRegionIDs(ma.SQLAlchemySchema):
    class Meta:
        model = dm.RetailSite
        load_instance = True
        include_relationships = False
    id = ma.auto_field()
    name = ma.auto_field()
    url_protocol = ma.auto_field()
    url_subdomain = ma.auto_field()
    url_domain = ma.auto_field()
    url_suffix = ma.auto_field()
    regions = fields.List(fields.Pluck(dm.Region.Schema(), "id"))

# class ExtensionScrapingRule(ma.Schema):
#     retail_site_id
#     default_rule
#     parent_elem_id
#     parent_id
#     class_chain # validate fully
#     items # if not a default rule (allow multiple in case of a form UI)
