"""
Test ScrapingRule model
"""

import pytest 
from sqlalchemy.exc import IntegrityError
from basketbot import datamodel as dm

def test_scraping_rule_default_constraints(db_with_items):
    """
    Check that scraping rules can only be default with no items or not default
    with at least one item
    """
    # Correct default rule
    sr = dm.ScrapingRule(
            default_rule=True,
            retail_site_id=dm.RetailSite.query.first().id,
            parent_elem_id=dm.DOMElem.query.first().id,
            parent_id ="test_id",
            class_chain = {}
            )
    db_with_items.add(sr)
    db_with_items.commit()
    sr_check = dm.ScrapingRule.query.get(sr.id)
    assert sr_check.default_rule
    assert len(sr_check.items) == 0

    # Correct non-default rule
    sr2 = dm.ScrapingRule(
            default_rule=False,
            retail_site_id=dm.RetailSite.query.first().id,
            parent_elem_id=dm.DOMElem.query.first().id,
            parent_id ="test_id",
            class_chain = {}
            )
    sr2.items = [dm.Item.query.first()]
    db_with_items.add(sr2)
    db_with_items.commit()
    sr2_check = dm.ScrapingRule.query.get(sr2.id)
    assert not sr2_check.default_rule
    assert len(sr2_check.items) == 1

    # Default rule with items
    with pytest.raises(IntegrityError):
        sr3 = dm.ScrapingRule(
                default_rule=True,
                retail_site_id=dm.RetailSite.query.first().id,
                parent_elem_id=dm.DOMElem.query.first().id,
                parent_id ="test_id",
                class_chain = {}
                )
        sr3.items = [dm.Item.query.first()]
        db_with_items.add(sr3)
        db_with_items.commit()
    db_with_items.rollback()

    # Non-default rule that does not specify any items
    with pytest.raises(IntegrityError):
        sr4 = dm.ScrapingRule(
                default_rule=False,
                retail_site_id=dm.RetailSite.query.first().id,
                parent_elem_id=dm.DOMElem.query.first().id,
                parent_id ="test_id",
                class_chain = {}
                )
        db_with_items.add(sr4)
        db_with_items.commit()
    db_with_items.rollback()

    # Existing default rule that attempts to add items
    with pytest.raises(IntegrityError):
        sr_check.items = [dm.Item.query.first()]
        db_with_items.add(sr_check)
        db_with_items.commit()
    db_with_items.rollback()

    # Existing non-default rule that attempts to remove items
    with pytest.raises(IntegrityError):
        sr2_check.items = []
        db_with_items.add(sr2_check)
        db_with_items.commit()
    db_with_items.rollback()


