from basketbot import ma
from basketbot.datamodel import User
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class TestSchema(ma.Schema):
    val = ma.Int()
