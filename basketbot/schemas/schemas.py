from basketbot import ma
from basketbot.datamodels import User

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
