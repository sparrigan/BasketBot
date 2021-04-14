import sys, inspect
from enum import Enum
from flask import *

class DefaultRuleNotUnique(Exception):
    pass

class InvalidRetailSiteURL(Exception):
    def __init__(self, msg='Retail Site not found with specified URL', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

class InvalidClassChain(Exception):
    def __init__(self, msg='ClassChain in scraping rule is not valid', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

class InvalidDOMElem(Exception):
    def __init__(self, msg='DOM element is not recognised', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

class InvalidURL(Exception):
    def __init__(self, msg='URL could not be resolved to a valid website', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


# Build enum of all our custom errors (warning: brittle)
all_classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
BasketBotErrors = Enum(
        "BasketBotErrors",
        dict([x for x in all_classes if issubclass(x[1], Exception)])
        )
