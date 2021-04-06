"""
Test RetailSite model
"""

import pytest
from basketbot import datamodel as dm
from basketbot import DefaultRuleNotUnique

def test_retail_site_get_item_rule(db_with_items):
    """
    Test that the get_item_rule method on RetailSite object
    correctly provides item exception rule or default rule
    """
    rs = dm.RetailSite.query.filter(dm.RetailSite.name=="Superstore").scalar()
    sr_1 = dm.ScrapingRule(
            default_rule=True,
            retail_site_id=rs.id,
            parent_elem_id=dm.DOMElem.query.first().id,
            parent_id ="testing_scraping_rule",
            class_chain = {}
            )
    sr_2 = dm.ScrapingRule(
            default_rule=False,
            retail_site_id=rs.id,
            parent_elem_id=dm.DOMElem.query.first().id,
            parent_id ="testing_scraping_rule_2",
            class_chain = {}
            )
    banana = dm.Item.query.filter(dm.Item.name=="banana").scalar()
    apple = dm.Item.query.filter(dm.Item.name=="apple").scalar()
    snapple = dm.Item.query.filter(dm.Item.name=="snapple").scalar()
    sr_2.items = [banana, apple]
    db_with_items.add_all([sr_1, sr_2])
    db_with_items.commit()
    assert rs.get_item_rule(banana) == sr_2
    assert rs.get_item_rule(apple) == sr_2
    assert rs.get_item_rule(snapple) == sr_1

def test_retail_site_scraping_attributes(db_with_items):
    """
    Test that the RetailSite ORM class attributes returns correct
    default and exception rules
    """
    # Test where have both defaults and exceptions
    rs = dm.RetailSite.query.filter(dm.RetailSite.name=="Superstore").scalar()
    sr_1 = dm.ScrapingRule(
            default_rule=True,
            retail_site_id=rs.id,
            parent_elem_id=dm.DOMElem.query.first().id,
            parent_id ="testing_scraping_rule",
            class_chain = {}
            )
    sr_2 = dm.ScrapingRule(
            default_rule=False,
            retail_site_id=rs.id,
            parent_elem_id=dm.DOMElem.query.first().id,
            parent_id ="testing_scraping_rule_2",
            class_chain = {}
            )
    sr_2.items = [
            dm.Item.query.filter(dm.Item.name=="banana").scalar(), 
            dm.Item.query.filter(dm.Item.name=="apple").scalar()
            ]
    db_with_items.add_all([sr_1, sr_2])
    db_with_items.commit()

    assert rs.default_rule == sr_1
    assert rs.exception_rules == [sr_2]

    # Test for error when have no or multiple default_rules associated
    rs2 = dm.RetailSite.query.filter(dm.RetailSite.name=="Megastore").scalar()
    assert rs2.exception_rules == []
    with pytest.raises(DefaultRuleNotUnique):
        rs2.default_rule
    db_with_items.rollback()
    sr_2.items = [] # NB: Important to clear items first as autoflush will raise...
    sr_2.default_rule = True # ... DefaultRuleNotUniquen prematurely here otherwise.
    db_with_items.add(sr_2)
    db_with_items.commit() # Associate two default rules with a store
    with pytest.raises(DefaultRuleNotUnique):
        rs.default_rule # This store now has two default scraping rules

@pytest.mark.parametrize("url",
        [
            (
                "http://www.superstore.com",
                True
                ), # In DB
            (
                "http://www.example.com",
                True
                ), # In DB
            (
                "http://www.superstore.com/products/2423452345",
                True
                ), # In DB (with extra path)
            (
                "http://www.superstore.com/products/4544?ra=45@la=55",
                True
                ), # In DB (with extra path and params)
            (
                "http://www.megastore.com/products/4544?ra=45@la=55",
                True
                ), # In DB (another entry)
            (
                "http://megastore.com/products/4544?ra=45@la=55",
                False
                ), # (lack of) subdomain not in DB 
            (
                "http://www.crinklefunk.com",
                False
                ), # Domain not in DB
            (
                "https://www.megastore.com/products/4544?ra=45@la=55",
                False
                ), # Wrong protocol
            (
                "https://www.superstore.co.uk/products/4544?ra=45@la=55",
                False
                ), # Suffix not in DB
            ])
def test_check_site_url(db_with_items, url):
    """
    Check the RetailSite class method for finding sites by url elements
    """
    rslt = dm.RetailSite.check_site_url(url[0])
    if url[1]:
        assert len(rslt) == 1 and isinstance(rslt[0], dm.RetailSite)
    else:
        assert len(rslt) == 0


