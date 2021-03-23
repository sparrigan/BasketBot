from datetime import datetime as dtime, timedelta
import pytz
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, Numeric, Date, BigInteger, Sequence, DateTime, Table, Binary, Interval
from sqlalchemy.dialects.postgresql import JSONB, JSON
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

# Relations

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
    basket_price = Column(Numeric(precision=10,scale=2), nullable=True)
    update_time = db.Column(DateTime(timezone=True), nullable=False, default=now, index=True)
    country_id = Column(Integer, ForeignKey('country.id'))
    currency_id = Column(Integer, ForeignKey('currency.id'))

    currency = relationship('Currency', back_populates='regions')
    country = relationship('Country', back_populates='regions')
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

    url_params = relationship('ItemURL', back_populates='retail_site')

class ItemURL(Base):
    """
    Store an item URL. Generally should be constructed as a set of params 
    used with basket_base_url from related RetailSite entry.
    Also include a raw_url field for use in cases where the item URL cannot
    be parametrized.
    Note: Check Constraint used here to ensure XOR of params or raw_url.
    Not supported by (eg:) MySQL
    """
    __tablename__ = 'url_params'
    __table_args__ = (
            CheckConstraint('NOT(params is NULL AND raw_url is NULL)'), 
            )
    id = Column(Integer, primary_key=True)
    params = Column(SJSON)
    raw_url = Column(String(20832), unique=True)
    retail_site_id = Column(Integer, ForeignKey('retail_site.id'))

    retail_site = relationship('RetailSite', back_populates='url_params')

    @classmethod
    def construct_url(cls, base_url, params):
        """
        Construct a URL from basket base url and params JSON
        """

    def get_item_url(self):
        """
        Construct the items URL
        """
        if self.raw_url:
            return self.raw_url
        else:
            pass

class User(Base):
    """
    Contains information on a User, including web-app and web-extension
    credentials
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    password = Column(String(60))

    scraping_rules = relationship('ScrapingRule', back_populates='owner')

class ScrapingRule(Base):
    """
    Contains a serialized description of a prices location in the DOM in
    relation to the closest parent DOM element having a unique ID.
    """
    __tablename__ = 'scraping_rule'
    id = Column(Integer, primary_key=True)
    update_time = db.Column(DateTime(timezone=True), nullable=False, default=now, index=True)
    owner = Column(Integer, ForeignKey('user.id'))
    parent_id = Column(Text)
    dom_chain = Column(SJSON)

    owner = relationship('User', back_populates='scraping_rules')

    def get_rule():
        """
        Convenience for extracting the formatted data needed for 
        traversing a DOM
        """
        pass
