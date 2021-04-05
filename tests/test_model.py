"""
Test that we can obtain required information from DB model
"""

import pytest
import validators
from sqlalchemy.exc import IntegrityError
from basketbot import datamodel as dm

def test_basket_version_update_on_addition(db_with_items):
    """
    Test that adding an item updates the basket versions
    of affected regions
    necessary basket versions in regions
    """
    # Check for basket_version update when items have names changed
    items = dm.Item.query.all()
    all_regions = dm.Region.query.all()
    updated_regions = set()
    for item in items:
        item.name += "_edited"
        updated_regions.update(item.regions)
    init_versions = {region.name: region.basket_version for region in all_regions}
    db_with_items.add_all(items)
    db_with_items.commit()
    # Require that affected regions have updated basket versions
    check_region_basket_versions(updated_regions, all_regions, init_versions)
    # Require that no other regions have been updated

    # Check for version updates when items move region 
    region_1 = dm.Region.query.filter(dm.Region.name=='Pripyat').scalar()
    region_2 = dm.Region.query.filter(dm.Region.name=='Birmingham').scalar()
    items_2 = region_2.items
    init_versions = {region.name: region.basket_version for region in all_regions}
    for item in items_2:
        item.regions = [region_1]
    db_with_items.add_all(items_2)
    db_with_items.commit()
    # Both regions should have updated versions as region 1 has
    # an item added to its basket, whilst region 2 has one removed
    check_region_basket_versions([region_1, region_2], all_regions, init_versions)

    # Check for version update when an item has more regions added
    region_3 = dm.Region.query.filter(dm.Region.name=='London').scalar()
    items_3 = region_3.items
    init_versions = {region.name: region.basket_version for region in all_regions}
    for item in items_3:
        item.regions += [region_1]
    db_with_items.add_all(items_3)
    db_with_items.commit()
    check_region_basket_versions([region_1, region_3], all_regions, init_versions)

    # Check for version update when items are added 
    item = dm.Item(name="chocolate carrots")
    item.regions=[region_2, region_3]
    init_versions = {region.name: region.basket_version for region in all_regions}
    db_with_items.add(item)
    db_with_items.commit()
    check_region_basket_versions([region_2, region_3], all_regions, init_versions)

    # Check for version update when items are deleted
    init_versions = {region.name: region.basket_version for region in all_regions}
    db_with_items.delete(item)
    db_with_items.commit()
    check_region_basket_versions([region_2, region_3], all_regions, init_versions)

def test_scraping_rule_default_constraints(db_with_items):
    """
    Check that scraping rules can only be default with no items or not default
    with at least one item
    """
    # Correct default rule
    sr = dm.ScrapingRule(
            default_rule=True,
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



def check_region_basket_versions(updated_regions, all_regions, init_versions):
    """
    Short Summary
    -------------
    Check whether basket_versions of affected regions are incremented.

    Extended Summary
    ----------------
    Enforces an assertion for affected regions to have their basket_version 
    values incremented by one, and for other regions to have identical basket_versions

    Parameters
    ----------
    updated_regions : list(basketbot.datamodel.Region)
        List of regions which should have incremented basket_version values
    all_regions : list(basketbot.datamodel.Region)
        List of all regions in the database
    init_versions : dict(str:int)
        Dictionary where keys are name attributes of Region objects and keys are 
        integers showing the basket_version of that region before any changes
    """
    for region in updated_regions:
        assert region.basket_version == init_versions[region.name] + 1
    for region in [r for r in all_regions if r not in updated_regions]:
        assert region.basket_version == init_versions[region.name]

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
    Check the RegionSite class method for finding sites by url elements
    """
    rslt = dm.RetailSite.check_site_url(url[0])
    if url[1]:
        assert len(rslt) == 1 and isinstance(rslt[0], dm.RetailSite)
    else:
        assert len(rslt) == 0

# def test_region_price(database):
#     """
#     Check for method returning basket price for a region 
#     """
#     pass
