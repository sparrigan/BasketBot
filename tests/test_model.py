"""
Test that we can obtain required information from DB model
"""

import validators
from basketbot import datamodel as dm
# from basketbot.util import url_check
#
# def test_ext(db_session):
#     item = dm.Item(name="testing")
#     item.regions = [dm.Region()]
#     db_session.add(item)
#     db_session.commit()
#
#     results = dm.Item.query.all()
#     assert len(results)==1
#
# def test_ext2(db_session):
#     results = dm.Item.query.all()
#     assert len(results)==0
#
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

# def test_scraping_url(database):
#     """
#     Check for method returning valid item URLs
#     """
#     item_urls = dm.ItemURL.query.all()
#     for item_url in item_urls:
#         url = item_url.get_item_url()
#         assert validators.url()
#
# def test_region_price(database):
#     """
#     Check for method returning basket price for a region 
#     """
#     pass

# def test_updating_basket_version()
