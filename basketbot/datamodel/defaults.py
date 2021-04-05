from basketbot import db
from basketbot import datamodel as dm

def create(session):
    """ Populate DB with default values """
    dom_elems = [
            dm.DOMElem(bs_name='div', js_name='DIV'),
            dm.DOMElem(bs_name='a', js_name='A'),
            dm.DOMElem(bs_name='br', js_name='BR')
            ]
    session.add_all(dom_elems)
    session.commit()

def create_test_defaults(session):
    """ Populate DB with test default values """
    # Countries
    country_1 = dm.Country(name="Ukraine")
    country_2 = dm.Country(name="England")
    # Currencies
    currency_1 = dm.Currency(name="Hryvnia", abbreviation="HRN")
    currency_2 = dm.Currency(name="Pound", abbreviation="GBP")
    # Regions
    region_1 = dm.Region(
            name="Pripyat",
            basket_price=45.33,
            basket_version=1
            )
    region_1.country = country_1
    region_1.currency = currency_1
    region_2 = dm.Region(
            name="Birmingham",
            basket_price=124.34,
            basket_version=1
            )
    region_2.country = country_2
    region_2.currency = currency_2
    region_3 = dm.Region(
            name="London",
            basket_price=14445.99,
            basket_version=1
            )
    region_3.country = country_2
    region_3.currency = currency_2
    # Retail sites
    retail_site_1 = dm.RetailSite(
            name="Superstore",
            url_domain="superstore",
            url_subdomain="www",
            url_suffix="com",
            url_protocol="http",
            basket_url="http://buy.superstore.com",
            basket_version=1,
            basket={"banana": 33.22, "apple": 44.22}
            )
    retail_site_2 = dm.RetailSite(
            name="Megastore",
            url_domain="megastore",
            url_subdomain="www",
            url_suffix="com",
            url_protocol="http",
            basket_url="http://buy.megastore.com",
            basket_version=1,
            basket={"snapple": 33.22, "juices": 44.22}
            )
    retail_site_3 = dm.RetailSite(
            name="Test site",
            url_domain="example",
            url_subdomain="www",
            url_suffix="com",
            url_protocol="http",
            basket_url=None,
            basket_version=1,
            basket={"snapple": 33.22, "juices": 44.22}
            )
    region_1.retail_sites = [retail_site_1, retail_site_2]
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
    item_5 = dm.Item(
            name="snozzages",
            all_regions=False
            )
    item_6 = dm.Item(
            name="hummus",
            all_regions=False
            )
    item_7 = dm.Item(
            name="cats milk",
            all_regions=False
            )
    item_1.regions = [region_1]
    item_2.regions = [region_1]
    item_3.regions = [region_1]
    item_4.regions = [region_2]
    item_5.regions = [region_2]
    item_6.regions = [region_3]
    item_7.regions = [region_3]
    session.add_all([
        country_1, country_2,
        region_1, region_2, region_3,
        currency_1, currency_2,
        retail_site_1, retail_site_2, retail_site_3,
        item_1, item_2, item_3, item_4, item_5, item_6, item_7
        ])
    session.commit()

