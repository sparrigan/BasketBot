from datetime import datetime as dtime, timedelta
import pytz
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, Date, BigInteger, Sequence, DateTime, Table, Binary, Interval
from sqlalchemy.dialects.postgresql import JSONB, JSON
from basketbot import db

def now():
    """ Useful helper for getting current time """
    return pytz.utc.localize(dtime.utcnow())

Base = db.Model

class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    rel_two = relationship('RelTwo', back_populates="rel_one")

class Region(Base):
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    basket_price = Column(String(100), unique=True)
    update_time = db.Column(DateTime(timezone=True), nullable=False, default=now, index=True)

    rel_one_id = Column(Integer, ForeignKey('rel_one.id'))
    rel_one = relationship('RelOne', back_populates="rel_two")
