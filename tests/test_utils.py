import pytest
import requests_mock
from basketbot import util
from basketbot.datamodel import model as dm

@pytest.mark.parametrize("url", [
    (
        'https://www.example.com',
        True
        ), # Already contains https
    (
        'https://www.example.com/param?test=example&test2=example2',
        True
        ), # Already contains https, has parameters
    (
        'https://example.com/param?test=example&test2=example2',
        True
        ), # Already contains https, no subdomain
    (
        'example_https.com',
        True
        ), # No protocol given, but requests mocked to return 200
    (
        'example_no_https.com',
        False
        ), # No protocol given, but requests mocked to return 200
    ])
def test_check_for_https(mocked_http_urls, url):
    assert util.check_for_https(url[0]) == url[1]

# @pytest.mark.usefixtures("mocked_http_urls")
@pytest.mark.parametrize("url", [
    (
        'https://www.example.com',
        ['https', 'www', 'example', 'com']
        ), 
    (
        'http://mail.mydomain.co.uk',
        ['http', 'mail', 'mydomain', 'co.uk']
        ), 
    (
        'https://www.example.com/param?test=example&test2=example2',
        ['https', 'www', 'example', 'com']
        ), 
    (
        'https://example.com/param?test=example&test2=example2',
        ['https', None, 'example', 'com']
        ), 
    (
        'example_https.com',
        ['https', None, 'example_https', 'com']
        ), 
    (
        'example_no_https.com',
        ['http', None, 'example_no_https', 'com']
        ),
    ])
@pytest.mark.usefixtures("mocked_http_urls")
class TestAddingURL:
    def test_decompose_url(self, url):
        rslt = util.decompose_url(url[0])
        assert [rslt['protocol'], rslt['subdomain'], rslt['domain'], rslt['suffix']] == url[1]

    def test_add_url_to_model(self, url):
        rs = dm.RetailSite(name="test")
        rs.add_site_url(url[0])
        assert [rs.url_protocol, rs.url_subdomain, rs.url_domain, rs.url_suffix] == url[1]

