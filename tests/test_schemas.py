import pytest
from basketbot.schemas import ScrapingRule
from marshmallow import ValidationError

@pytest.mark.parametrize("payload", [
    ({
        "parent_elem": "a",
        "parent_id": "swashbuckling",
        "class_chain": {
            "0": {"elem": "br", "classes": ["fandangaling", "jimminy"]},
            "1": {"elem": "div", "classes": ["goodness", "willickers"]}, 
        }},
        True
        ), # All is well
    ({
        "blah": "ra"
        },
        False
        ), # Completely failing at being a class-chain
    ({
        "parent_elem": "img",
        "parent_id": "swashbuckling",
        "class_chain": {
            "0": {"elem": "br", "classes": ["fandangaling", "jimminy"]},
            "1": {"elem": "div", "classes": ["goodness", "willickers"]}, 
        }},
        False
        ), # HTML elem not contained in DB
    ({
        "parent_elem": "DIV",
        "parent_id": "swashbuckling",
        "class_chain": {
            "0": {"elem": "br", "classes": ["fandangaling", "jimminy"]},
            "1": {"elem": "div", "classes": ["goodness", "willickers"]}, 
        }},
        False
        ), # HTML elem not adhering to capatilization of beautiful soup
    ({
        "parent_elem": "div",
        "parent_id": "swashbuckling",
        "class_chain": {
            "0": {"elem": "br", "classes": ["fandangaling", "jimminy"]},
            "one": {"elem": "div", "classes": ["goodness", "willickers"]}, 
            "two": {"elem": "div", "classes": ["goodness", "willickers"]}, 
            "three": {"elem": "div", "classes": ["goodness", "willickers"]}, 
        }},
        False
        ), # Class chain keys are not numeric
    ({
        "parent_elem": "div",
        "parent_id": "swashbuckling",
        "class_chain": {
            "0": {"elem": "br", "classes": ["fandangaling", "jimminy"]},
            "2": {"elem": "div", "classes": ["goodness", "willickers"]}, 
            "3": {"elem": "div", "classes": ["goodness", "willickers"]}, 
            "4": {"elem": "div", "classes": ["goodness", "willickers"]}, 
        }},
        False
        ), # Class chain keys do not increment 
    ({
        "parent_elem": "div",
        "parent_id": "swashbuckling",
        "class_chain": {
            "1": {"elem": "br", "classes": ["fandangaling", "jimminy"]},
            "2": {"elem": "div", "classes": ["goodness", "willickers"]}, 
            "3": {"elem": "div", "classes": ["goodness", "willickers"]}, 
            "4": {"elem": "div", "classes": ["goodness", "willickers"]}, 
        }},
        False
        ), # Class chain keys do not begin at zero 
    ({
        "parent_elem": "div",
        "parent_id": "swashbuckling",
        "class_chain": {
            "0": {"elem": "br", "classes": ["fandangaling", "jimminy"]},
            "1": {"elem": "rat", "classes": ["goodness", "willickers"]}, 
            "2": {"elem": "div", "classes": ["goodness", "willickers"]}, 
            "3": {"elem": "div", "classes": ["goodness", "willickers"]}, 
        }},
        False
        ), # HTML tag from ClassChain not contained in DB 
    ({
        "parent_elem": "div",
        "parent_id": "swashbuckling",
        "class_chain": {
            "0": {"elem": "br", "classes": ["fandangaling", "jimminy"]},
            "1": {"elem": "div", "classes": ["goodness", "willickers"]}, 
            "2": {"elem": "div", "classes": ["goodness", "willickers"]}, 
            "3": {"elem": "DIV", "classes": ["goodness", "willickers"]}, 
        }},
        False
        ), # HTML tag from ClassChain does not adhere to BS format 
    ({
        "parent_elem": "div",
        "parent_id": "swashbuckling",
        "class_chain": {
            "0": {"elem": "br", "classes": ["fandangaling", "jimminy"]},
            "1": {"elem": "div", "classes": "goodness"}, 
            "2": {"elem": "div", "classes": ["goodness", "willickers"]}, 
            "3": {"elem": "div", "classes": ["goodness", "willickers"]}, 
        }},
        False
        ), # A ClassChain has classes that are not a list
    ({
        "parent_elem": "div",
        "parent_id": "swashbuckling",
        "class_chain": {
            "0": {"elem": "br", "classes": ["fandangaling", "jimminy"]},
            "1": {"elem": "div", "classes": "goodness"}, 
            "2": {"elem": "div", "classes": ["goodness", "willickers"]}, 
            "3": {"elem": "div", "classes": [55, "willickers"]}, 
        }},
        False
        ) # A ClassChain has classes that are not strings
    ])
def test_scraping_rule_validator(payload):
    """
    Test whether API validator works for Scraping Rules
    """
    # Have to catch validation errors here
    scraping_rule = ScrapingRule(exclude=["update_time", "id"])
    payload, success = payload
    if success:
        assert scraping_rule.load(payload)
    else:
        with pytest.raises(ValidationError):
            scraping_rule.load(payload)
