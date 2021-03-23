"""
Test that we can obtain required information from DB model
"""

import validators
from basketbot import datamodel as dm
from basketbot.util import url_check

def test_scraping_url(database):
    """
    Check for method returning valid item URLs
    """
    item_urls = dm.ItemURL.query.all()
    for item_url in item_urls:
        url = item_url.get_item_url()
        assert validators.url()

def test_region_price(database):
    """
    Check for method returning basket price for a region 
    """
    pass
