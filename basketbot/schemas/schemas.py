from basketbot import ma
from basketbot.datamodel import model as dm
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import Schema, fields, ValidationError

def validate_dom_elem(check):
    """
    Short Summary
    -------------
    Check that a dom element string is contained in a bs_name value in the DB
    """
    known_elems = [x[0] for x in dm.DOMElem.query.with_entities(dm.DOMElem.bs_name)]
    if check not in known_elems:
        raise ValidationError("Provided Parent element does not match any element tag listed in basketbot DB")

def validate_class_chain(check):
    """
    Short Summary
    -------------
    Check that a class chain object contains correct structure and valid DOM elements
    """
    cce = ClassChainElem()
    keys = check.keys()
    check_keys = [x.isnumeric() for x in keys]
    if not all(check_keys):
        raise ValidationError("Provided ClassChain does not use numeric keys")
    if sorted(keys) != list(map(str, range(len(keys)))):
        raise ValidationError("Provided ClassChain does not contain incremented 0-based labels")
    check_values = [cce.validate(val) for val in check.values()]
    if sum(len(x) for x in check_values)>0:
        raise ValidationError(f"Failed to validate ClassChain contents with following errors: {check_values}")

class ClassChainElem(ma.Schema):
    elem = fields.Str(validate=validate_dom_elem)
    classes = fields.List(fields.Str())

class ScrapingRule(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = dm.ScrapingRule
        load_instance = True

    parent_elem = fields.Str(validate=validate_dom_elem)
    class_chain = fields.Raw(validate=validate_class_chain)

class SiteURL(ma.Schema):
    url = ma.Str()

class TestSchema(ma.Schema):
    val = ma.Int()
