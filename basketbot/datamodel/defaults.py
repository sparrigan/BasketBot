from basketbot import db
from basketbot import datamodel as dm

def create():
    """ Populate DB with default values """
    dom_elems = [
            dm.DOMElem(bs_name='div', js_name='DIV'),
            dm.DOMElem(bs_name='a', js_name='A')
            ]
    db.session.add_all(dom_elems)
    db.session.commit()

def create_test_defaults(session):
    """ Populate DB with test default values """
    # Countries
    country = dm.Country(name="Ukraine")
    # Currencies
    currency = dm.Currency(name="Hryvnia", abbreviation="HRN")
    # Regions
    region = dm.Region(
            name="Pripyat",
            basket_price=45.33,
            basket_version=1
            )
    region.country = country
    region.currency = currency
    # Retail sites
    retail_site_1 = dm.RetailSite(
            name="Superstore",
            url="http://www.superstore.com",
            basket_base_url="http://buy.superstore.com",
            basket_version=1,
            basket={"banana": 33.22, "apple": 44.22}
            )
    retail_site_2 = dm.RetailSite(
            name="Megastore",
            url="http://www.megastore.com",
            basket_base_url="http://buy.megastore.com",
            basket_version=1,
            basket={"snapple": 33.22, "juices": 44.22}
            )
    region.retail_sites = [retail_site_1, retail_site_2]
    # Items
    item_1 = dm.Item(
            name="apple",
            all_regions=True
            )
    item_2 = dm.Item(
            name="banana",
            all_regions=False
            )
    item_3 = dm.Item(
            name="snapple",
            all_regions=False
            )
    item_4 = dm.Item(
            name="juices",
            all_regions=False
            )
    item_1.regions = [region]
    item_2.regions = [region]
    item_3.regions = [region]
    item_4.regions = [region]
    session.add_all([country, region, currency, retail_site_1, retail_site_2, item_1, item_2, item_3, item_4])
    session.commit()

