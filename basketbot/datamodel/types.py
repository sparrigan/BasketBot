import json
from basketbot import db

class StringJSON(db.TypeDecorator):
    """Store JSON as string for engines not supporting JSON"""

    impl = db.TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

SJSON = db.JSON().with_variant(StringJSON, 'sqlite')

