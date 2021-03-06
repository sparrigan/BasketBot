## Model notes

### Baskets and items

#### Basket relation

A relation called `Basket` stores a list of items. Each row has an `ID`, `name` and a list of associated Regions (a many-many key via a tertiary table to the `Region` table). This table keeps track of what items are currently considered to constitute a basket for a given region. Note that this relation also has an `all_regions` boolean value. If this is set to `True` then any new Region added to the `Region` relation will automatically be associated with this Item (i.e. we are saying that this item is a 'default' for all regions in the world).

#### Retail_site relation

For every retail_site in some region `r_id` we must store information for every item in that regions basket  (i.e every item found according to `SELECT * from Basket WHERE region_id=r_id`). In particular we need to store: the current item's price, and a URL and associated Scraping rule for getting that price again in the future. This information is stored in the `RetailSite` relation, in a JSON `basket` column. The JSON is of the form 

```
{
    "<item_name_1>": 
        {"URL": "http://...",
        "Price": 34.34}
    "<item_name_2>": 
        {"URL": "http://...",
        "Price": 35.32},
        ...
    }
```

Note that here the only component of a 'scraping rule' that differs between items is the URL for that item. In future we might want to also allow a specification of a different scraping rule (i.e. parentID an class_chain etc...) for each item.
Another column in `RetailSite` is called `basket_version`, and this records the version of the basket for this region that the JSON in `basket` currently holds information for.

#### Basket_version relation (and associated HistorialBaskets relation)

We keep track of what is the most recent version of a basket in the `BasketVersion` table, which has columns `Region`, `Version` and `update_time` (the latter keeps track of when the version was last updated for a given region). This is used as an intermediary to ensure that the schemaless JSON data in the `RetailSite` is kept concurrent with the items in the `Basket` relation. This is done with some triggers:

* When a new item is added or removed from the `Basket` relation, then the following is triggered:
    * The value of `Version` for this Region in the `BasketVersion` relation is incremented, and the `update_time` is also reset.
    * The old basket data for this region (i.e. `SELECT * FROM basket WHERE region=r_id` ran prior to the update) is serialized into a JSON and stored in the `HistoricalBaskets` relation, along with its version number, the previous update_time (i.e. when this old version was first added, and the new update_time (i.e. when this version stopped being used. So `HistoricalBaskets` has the columns `Region`, `Version_number`, `Added_date`, `Removed_date`, `basket` (the last column being the JSON store of old basket items).
    * A check is ran to find any rows from the `Retail_site` relation in the updated region which have baskets associated with older versions (by looking at their `basket_version` column value. A maintainer is alerted (via slack/email/carrier pigeon etc...) to the retail_sites with out-of-date baskets that need to be updated.

Note also that a join from `Retail_store` to basket on region is used to validate any future JSON baskets inserted into `RetailStore` to ensure data integrity.

Note: Currently `RetailSite` has a unique url. May need to instead have (region, url) pair as unique.

#### Associating Scraping Rules with Retail Sites and Items

This can probably be improved, but at the moment we have a `ScrapingRule` table that has a many-one relationship to the `RetailSite` table. i.e. a Retail Site can have many different scraping rules, but a given scraping rule is only associated with one retail site. A site can have more than one scraping rule because potentially different items on the site may have different scraping rules.

`ScrapingRule` entries can also have a many-one relationship with the `Item` table. i.e. a scraping rule can only be associated with (at most) one Item, but an Item may be associated with many scraping rules (as an Item can be scraped from many different retail sites).

We want to handle two possible cases.

1. That there is a single scraping rule that applies to all, or multiple items on a retail site
2. There are some items that have their own specific scraping rules for a site.

Correspondingly there are two kinds of scraping rule that might be associated with a retail site - a default one, and also 'exceptions' that apply for specific items, which should be used with higher precedence than the default scraping rule.

We deal with this as follows:
* There is a `default` boolean column in the `ScrapingRule` table. If this is `True` then the rule is applied to any item for a retail site that does not have a specific exclusion rule. 
* There is a constraint on the `ScrapingRule` table such that if `default=True` then there must not be any items in the rules many-many item relationship.
* `RetailSite` has a one-many relationship with `ScrapingRule` called `scraping_rules` that keeps track of all scraping rules associated with that retail site (whether they be the default rule or the exception rules).
* The `RetailSite` ORM object exposes two properties - `default_rule` and `exceptions`. These each access the `scraping_rules` relation and filter out all but the default rule or expections respectively.
* A method on `RetailSite` called `get_item_rule(item_id)`, can be passed an items ID (or just a plain ORM `Item` object) and will use the above two properties to either return the specific exception rule for that item for this retail site, or - if no exception is found for this item - will return the default scraping rule for the retail site.

Important points of note/future work:

1. A lot of the above logic would be a lot nicer as DB triggers and SQL queries, rather than ORM logic.

2. Note that we do not currently have a way of ensuring that a default rule always exists for a retail site. We can't really make the `default_rule` relation on `RegionSite` `NOT NULL`, because often someone will probably create a site in the DB and then go and set a scrape rule for it. It would however be nice to ensure this integrity.

3. Currently we do not have any constraint to ensure that the items that a `ScrapingRule` lists in it's exclusion are from the same `Region` as the `RetailSite` that the `ScrapingRule` is associated with. A `ScrapingRule` should never be referring to `Items` that its `RetailStore` can't have in its basket. We should maybe enforce this

4. If an Item is removed from a region, then along with the various `basket_version` updates we do on event listeners, we should probably also somehow remove or at least flag `ScrapingRules` that apply only to those items in a region that they are no longer associated with (so long as they are not associated with any other items that are still valid in the region of the retail store that the scraping rule applies to). 


## Security

# User auth

* First pass simply uses cookie-based session auth, implemented via [Flask-Security](https://pythonhosted.org/Flask-Security/). In future better to move to JWT to scale more easily and allow mobile. This may require some refactoring of the `User` and `Role` relations in DB schema. See eg: [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/en/stable/) or [this guide](https://realpython.com/token-based-authentication-with-flask/) for an intro into JWT-based auth.

# HTTPS

* No certification currently used. See [here](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https) for info on how to serve Flask app over HTTPS.

# CSRF

* If roll a demo with cookie-based sessions then need to configure CSRF, as outlined [here](https://testdriven.io/blog/csrf-flask/).


# TODO:

* When checking to see whether a retail sites base url is currently in the database (and when storing them) we currently use the util at basketbot.util.scraping.get_base_url, but this returns the host including a subdomain (eg www in www.example.com). Maybe we should only include hostname (eg example.com)
