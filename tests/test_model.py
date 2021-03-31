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
    items = dm.Item.query.all()
    regions = set()
    for item in items:
        item.name += "_edited"
        regions.update(item.regions)
    init_versions = {region.name: region.basket_version for region in regions}
    db_with_items.add_all(items)
    db_with_items.commit()
    region = dm.Region.query.first()
    print("Versions")
    print(init_versions)
    print(region.basket_version)



    # Add items from other regions
    # Add items that are associated with more than one region




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
