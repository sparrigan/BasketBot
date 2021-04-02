from datetime import datetime as dtime, timedelta
import pytz
from sqlalchemy import ForeignKey, CheckConstraint, event, inspect
from sqlalchemy.orm import relationship, backref, mapper
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, Numeric, Date, BigInteger, Sequence, DateTime, Table, Binary, Interval
from sqlalchemy.dialects.postgresql import JSONB, JSON
from flask_security import UserMixin, RoleMixin
from basketbot import db
from basketbot.datamodel.types import SJSON

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
    and basket_base_url is the API base for obtaining items with relevant params
    """
    __tablename__ = 'retail_site'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    url = Column(String(20832), unique=True)
    basket_base_url = Column(String(20832), unique=True)
    basket_version = Column(Integer)
    basket = Column(SJSON)

    # url_params = relationship('ItemURL', back_populates='retail_site')

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
    id = Column(Integer, primary_key=True)
    update_time = db.Column(DateTime(timezone=True), nullable=False, default=now, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    parent_elem_id = Column(Integer, ForeignKey('dom_elem.id'))
    parent_id = Column(Text)
    class_chain = Column(SJSON)

    parent_elem = relationship('DOMElem')
    user = relationship('User', back_populates='scraping_rules')

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

# Events

# This listener needs to be added here to catch the mapper config trigger
# early enough
from basketbot.util.db import setup_schema
event.listen(mapper, "after_configured", setup_schema(Base, db.session))

# Note that these functions are defined here, but actually registered
# in main basketbot __init__. This encapsulation allows also registering
# events easily on pytest stateless DB sessions
def register_events(session):
    SESSION_INFO_KEY = 'altered_regions'

    # Autogenerate marshmallow schemas from model
    # from basketbot.schemas import setup_schema
    # event.listen(mapper, "after_configured", setup_schema(base, session))

    @event.listens_for(session, "before_flush")
    def check_for_items(session, flush_context, instances):
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
