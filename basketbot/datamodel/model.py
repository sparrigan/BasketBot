from datetime import datetime as dtime, timedelta
import pytz
from sqlalchemy import ForeignKey, CheckConstraint, event, inspect, and_
from sqlalchemy.orm import relationship, backref, mapper, configure_mappers
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, Numeric, Date, BigInteger, Sequence, DateTime, Table, Binary, Interval
from sqlalchemy.dialects.postgresql import JSONB, JSON
from flask_security import UserMixin, RoleMixin
from basketbot import db, DefaultRuleNotUnique
from basketbot.datamodel.types import SJSON
from basketbot.util import setup_schema, decompose_url

# Helpers

def now():
    """ Useful helper for getting current time """
    return pytz.utc.localize(dtime.utcnow())

Base = db.Model


# Association tables

# Regions <-> RetailSites
RegionRetailSite = Table('regions_retail_sites', Base.metadata,
    Column('region_id', Integer, ForeignKey('region.id')),
    Column('retail_site_id', Integer, ForeignKey('retail_site.id'))
)

# Regions <-> Items
RegionItem = Table('regions_items', Base.metadata,
    Column('region_id', Integer, ForeignKey('region.id')),
    Column('item_id', Integer, ForeignKey('item.id'))
)

# Roles <-> Users
class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))

# Scraping Rules <-> Items (for non-default scraping rules)
ScrapingRuleItem = Table('scraping_rule_item', Base.metadata,
        Column('scraping_rule_id', Integer, ForeignKey('scraping_rule.id')),
        Column('item_id', Integer, ForeignKey('item.id'))
        )

# Relations

class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(255))
    password = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))

    scraping_rules = relationship('ScrapingRule', back_populates='user')

class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)

    regions = relationship('Region', back_populates='country')

class Currency(Base):
    __tablename__ = 'currency'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    abbreviation = Column(String(3), unique=True)

    regions = relationship('Region', back_populates='currency')
    conversion_rates = relationship('ConversionRate', back_populates='currency')

class ConversionRate(Base):
    __tablename__ = 'conversion_rate'
    id = Column(Integer, primary_key=True)
    currency_id = Column(Integer, ForeignKey('currency.id'))
    rate = Column(Float(), nullable=False)

    currency = relationship('Currency', back_populates='conversion_rates')

class Region(Base):
    """
    Note that the basket price is given in USD. To determine local 
    currency conversion, match update_time to corresponding conversion
    rate in ConversionRate
    """
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    update_time = db.Column(DateTime(timezone=True), nullable=False, default=now, index=True)
    country_id = Column(Integer, ForeignKey('country.id'))
    currency_id = Column(Integer, ForeignKey('currency.id'))
    basket_price = Column(Numeric(precision=10,scale=2), nullable=True)
    basket_version = Column(Integer, nullable=False)
    basket_version_update_time = db.Column(DateTime(timezone=True), nullable=False, default=now, index=True)

    currency = relationship('Currency', back_populates='regions')
    country = relationship('Country', back_populates='regions')
    historical_baskets = relationship('HistoricalBaskets', back_populates='region')
    # Note that backref automatically creates reverse relationship on RetailSite
    retail_sites = relationship('RetailSite',
            secondary=RegionRetailSite,
            backref='regions')

    def get_basket_local(self):
        """
        Short Summary
        -------------
        Determine the local value of the regions current basket price using
        current conversion rate.
        """
        pass

class RetailSite(Base):
    """
    Stores information on retail web-sites, including assciated regions
    and base url information. Note that url column is the websites base url,
    and basket_url is the retail sites API base for obtaining items with relevant params
    """
    __tablename__ = 'retail_site'
    # Require retail site urls to be unique wrt subdomain+domain+suffix
    __table_args__ = (
            UniqueConstraint(
                'url_domain',
                'url_subdomain',
                'url_suffix',
                name='_retail_site_url_uc'
                ),
            )
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    url_protocol = Column(String(253), nullable=True)
    url_subdomain = Column(String(253), nullable=True) # Not all URLS have a subdomain
    url_domain = Column(String(253), nullable=False)
    url_suffix = Column(String(253), nullable=False)
    basket_url = Column(String(20832), nullable=True)
    basket_version = Column(Integer)
    basket = Column(SJSON)

    scraping_rules = relationship('ScrapingRule', back_populates='retail_site')

    @property
    def default_rule(self):
        """
        Short Summary
        -------------
        Get the default scraping rule associated with this retail website 
        """
        rule = [rule for rule in self.scraping_rules if rule.default_rule] 
        if len(rule)==0:
            raise DefaultRuleNotUnique(f'Retail site {self.id} does not have an associated default scraping rule')
        elif len(rule)>1:
            raise DefaultRuleNotUnique(f'Retail site {self.id} is associated with more than one default scraping rule')
        else:
            return rule[0]

    @property
    def exception_rules(self):
        """
        Short Summary
        -------------
        Get scraping rules associated with specific items for this site
        (i.e. all non-default rules)
        """
        return [rule for rule in self.scraping_rules if not rule.default_rule] 

    def get_item_rule(self, item):
        """
        Short Summary
        -------------
        Get scraping rule for a particular item for this retail site

        Extended Summary
        ----------------
        When passed a basketbot.datamodel.Item ORM object, or integer Item ID, 
        find the scraping rule for this object. If there is a specific 
        exception rule for this item then this is returned. If not then
        the default rule is returned. If neither is available then an error
        is thrown
        """
        # Get the item ID
        item_id = item if isinstance(item, int) else item.id
        # Should really be doing all this DB side
        exception_rule = [r for r in self.exception_rules if item_id in map(lambda x: x.id, r.items)]
        return exception_rule[0] if len(exception_rule)==1 else self.default_rule

    # url_params = relationship('ItemURL', back_populates='retail_site')

    def add_site_url(self, url_str):
        """
        Short Summary
        -------------
        This method should be used to add a url from a string, as will decompose
        into various components
        """
        rslt = decompose_url(url_str)
        self.url_protocol = rslt['protocol']
        self.url_subdomain = rslt['subdomain']
        self.url_domain = rslt['domain']
        self.url_suffix = rslt['suffix']


    @classmethod
    def check_site_url(cls, url_str):
        """
        Short Summary
        -------------
        Takes a URL string, extracts the base URL (if necessary)
        and then compares for entries in DB
        """
        rslt = decompose_url(url_str)
        sites = cls.query.filter(and_(
            cls.url_protocol == rslt['protocol'],
            cls.url_subdomain == rslt['subdomain'],
            cls.url_domain == rslt['domain'],
            cls.url_suffix == rslt['suffix'],
            )).all()
        return sites

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    all_regions = Column(Boolean, default=False)
    regions = relationship('Region',
            secondary=RegionItem,
            backref='items')

@event.listens_for(Item, "before_insert")
@event.listens_for(Item, "before_update")
def check_item_for_region(mapper, connection, target):
    """
    Ensure that an Item is inserted with an associated region
    """
    if not any([isinstance(r, Region) for r in target.regions]):
        raise IntegrityError("Item objects must contain at least one Region object in their region relationship", None, None)

class HistoricalBaskets(Base):
    __tablename__ = 'historical_baskets'
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey('region.id'))
    basket = Column(SJSON, nullable=False)

    region = relationship('Region', back_populates='historical_baskets', uselist=None)

# class ItemURL(Base):
#     """
#     Store an item URL. Generally should be constructed as a set of params 
#     used with basket_base_url from related RetailSite entry.
#     Also include a raw_url field for use in cases where the item URL cannot
#     be parametrized.
#     Note: Check Constraint used here to ensure XOR of params or raw_url.
#     Not supported by (eg:) MySQL
#     """
#     __tablename__ = 'url_params'
#     __table_args__ = (
#             CheckConstraint('NOT(params is NULL AND raw_url is NULL)'), 
#             )
#     id = Column(Integer, primary_key=True)
#     params = Column(SJSON)
#     raw_url = Column(String(20832), unique=True)
#     retail_site_id = Column(Integer, ForeignKey('retail_site.id'))
#
#     retail_site = relationship('RetailSite', back_populates='url_params')
#
#     @classmethod
#     def construct_url(cls, base_url, params):
#         """
#         Construct a URL from basket base url and params JSON
#         """
#
#     def get_item_url(self):
#         """
#         Construct the items URL
#         """
#         if self.raw_url:
#             return self.raw_url
#         else:
#             pass
#
class DOMElem(Base):
    """
    Short Summary
    -------------
    A lookup table for representing all DOM elements that scraper can handle.
    Also includes a translation between beautifulsoup and JS tag representations
    """
    __tablename__ = 'dom_elem'
    id = Column(Integer, primary_key=True)
    bs_name = Column(String(10))
    js_name = Column(String(10))

    @classmethod
    def get_lookup_table(cls, js_first=True):
        """
        Short Summary
        -------------
        Generate a dictionary lookup table for converting between
        all accepted beautifulsoup and javascript tag notations

        Parameters
        ----------
        js_first : bool
            If True then dict has JS notations as keys, if False then
            BS notations are keys (default: True)
        """
        elems = cls.query.all()
        if js_first:
            return {elem.js_name: elem.bs_name}
        else:
            return {elem.bs_name: elem.js_name}

class ScrapingRule(Base):
    """
    Short Summary
    -------------
    Contains a serialized description of a prices location in the DOM in
    relation to the closest parent DOM element having a unique ID.

    Extended Summary
    ----------------
    Scraping rules are stored as follows:
    parent_elem - stores the name of the parent element used in the scraping rule. 
    This is the starting node in the tree that will be used for scraping (the first 
    element above the element to be scraped that has an ID). Note that is a relation to 
    dom_element table.
    parent_id - the string ID of the parent DOM element used to start the scrape
    class_chain - A JSON containing a list of DOM tree nodes to traverse down,
    starting from the parent element. of the form: 
    {
        "<tree_level>": 
            {
                "elem": "<elem_name>",
                "classes": ["<class_1>", "<class_2>",...]
            }
    }
    Note that <tree_level> starts at 0 for nodes immediately below the parent element in 
    the DOM tree. <elem_name> is a BS compliant element name string. Class chains are 
    validated at the app-level to ensure that elem values are strings contained in the
    bs_name field of the dom_elem relation.
    """
    __tablename__ = 'scraping_rule'
    # __table_args__ = (
    #         # Require that if scraping rule is a default then it has no item relations
    #         CheckConstraint('NOT(default=1 AND parent_elem_id!=1)'), 
    #         )
    id = Column(Integer, primary_key=True)
    update_time = db.Column(DateTime(timezone=True), nullable=False, default=now, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    retail_site_id = Column(Integer, ForeignKey('retail_site.id'), nullable=False)
    default_rule = Column(Boolean, default=False, nullable=False)
    parent_elem_id = Column(Integer, ForeignKey('dom_elem.id'), nullable=False)
    parent_id = Column(Text)
    class_chain = Column(SJSON, nullable=False)

    parent_elem = relationship('DOMElem')
    user = relationship('User', back_populates='scraping_rules')
    retail_site = relationship('RetailSite', back_populates='scraping_rules')
    items = relationship(
            'Item', 
            secondary=ScrapingRuleItem,
            backref='scraping_rules'
            )


    @classmethod
    def create_rule():
        """
        Short Summary
        -------------
        Method for creating a new Scraping rule entry. Note that this should be
        used rather than direct DB access, as element names may need conversion
        from JS to BS notation.
        """
        pass

    def get_rule():
        """
        Convenience for extracting the formatted data needed for 
        traversing a DOM
        """
        pass


# This listener needs to be added here to catch the mapper config trigger
# early enough
event.listen(mapper, "after_configured", setup_schema(Base, db.session))
configure_mappers() # No idea why we need to manually call this

# Events

# Note that these functions are defined here, but actually registered
# in main basketbot __init__. This encapsulation allows also registering
# events easily on pytest stateless DB sessions
def register_events(session):
    SESSION_INFO_KEY = 'altered_regions'

    # Autogenerate marshmallow schemas from model
    # from basketbot.schemas import setup_schema
    # event.listen(mapper, "after_configured", setup_schema(base, session))

    @event.listens_for(ScrapingRule, "before_insert")
    @event.listens_for(ScrapingRule, "before_update")
    def check_scraping_rule_for_default(mapper, connection, target):
        """
        Ensure that a ScrapingRule with default=True is not associated with any specific items
        """
        if target.default_rule and len(target.items)>0:
            raise IntegrityError("Scraping Rule cannot be set as default_rule for a retail site and also be related to specific items", None, None)
        if (not target.default_rule) and len(target.items)==0:
            raise IntegrityError("A non-default_rule Scraping Rule must be related to at least one item", None, None)
    # We should really also do a check for when Items are inserted too in case one is associated with
    # a scraping rule from the other side

    # Changed this from before_flush to after_flush as could not resolve some
    # relations in before_flush (no autocommit?)
    # @event.listens_for(session, "before_flush")
    # def check_for_items(session, flush_context, instance):
    @event.listens_for(session, "after_flush")
    def check_for_items(session, flush_context):
        """
        Detect whether any items have been altered or addded during a flush
        and take a note of their regions in the Session.info dict
        """
        altered_regions = set()
        for _ in session.new.union(session.dirty):
            if isinstance(_, Item):
                state = inspect(_)
                # Flag any regions with changed item names or new items
                # NB: state.attrs.name.histroy.added also catches new items
                if len(state.attrs.name.history.added)>0 or len(state.attrs.regions.history.added)>0:
                    altered_regions.update(_.regions)
                # Flag any regions removed from item
                if len(state.attrs.regions.history.deleted)>0:
                    altered_regions.update(state.attrs.regions.history.deleted)
        for _ in session.deleted:
            # Flag any regions with deleted items
            if isinstance(_, Item):
                altered_regions.update(_.regions)
        if SESSION_INFO_KEY in session.info:
            session.info[SESSION_INFO_KEY].update(altered_regions)
        else:
            session.info[SESSION_INFO_KEY] = altered_regions

    @event.listens_for(session, "after_rollback")
    def remove_items(session):
        """
        Remove any altered regions from Session.info dict, as there has been
        a rollback
        """
        if SESSION_INFO_KEY in session.info:
            del session.info[SESSION_INFO_KEY]

    @event.listens_for(session, "before_commit")
    def update_basket_versions(session):
    # def update_basket_version(session, flush_context, instances):
        """
        Using the list of regions stored in Session.info dict, update the
        basket_versions for these regions, as some of their basket items have
        been added/edited.
        """
        session.flush() # see https://stackoverflow.com/a/36732359 for why this is here
        # Should really optimize this all if it's going to run on every
        # session flush (DB trigger?)
        # altered_regions = set()
        # for _ in session.new.union(session.dirty):
        #     if isinstance(_, Item):
        #         altered_regions.update(_.region)

        if len(altered_regions:=session.info.get(SESSION_INFO_KEY, set()))>0:
            for region in altered_regions:
                region.basket_version += 1
                # Trigger alerts for any regions with updated basket_versions
                # could go here if there is not also an update in this commit 
                # for their baskets
            session.add_all(altered_regions)
            # session.commit()
            # session.flush()

        # Make sure to clear altered_regions from session.info
        if SESSION_INFO_KEY in session.info:
            del session.info[SESSION_INFO_KEY]
