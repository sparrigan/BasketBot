import pytest
from marshmallow import ValidationError
from basketbot import BasketBotErrors
from basketbot.schemas import ExtensionScrapingRule

def test_scraping_rule_schema(db_with_items, scraping_rule_schema_data):
    """
    Check that test objects are validated and fail as expected.
    NOTE: Maybe should do some customization with pytest.fail here
    to better report errors. Can use `message` argument to pytest.raises
    if necessary
    """
    esr = ExtensionScrapingRule()
    data, error = scraping_rule_schema_data
    if error is None:
        assert esr.load(data)
    else:
        with pytest.raises(BasketBotErrors[error].value):
            esr.load(data)
