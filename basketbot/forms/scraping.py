from flask_wtf import FlaskForm
from wtforms.fields import StringField

class ScrapingRuleForm(FlaskForm):
    items = StringField('items')
