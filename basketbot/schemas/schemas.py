from basketbot import ma
from basketbot.datamodel import User

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class TestSchema(ma.Schema):
    val = ma.Int()
