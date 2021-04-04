from urllib.parse import urlparse
import requests
import tldextract

def decompose_url(url_str):
    """
    Short Summary
    -------------
    Get the base URL domain from a passed URL string

    Extended Summary
    ----------------
    Note that at the moment we include a subdomain (eg: www in www.example.com).
    But maybe we should only be storing and comparing the host (eg: example.com).
    A simple additional regex after the use of netloc could fix this.
    """
    # Extract protocol, or determine it if necessary
    if 'http://' in url_str:
        protocol = 'http'
    elif 'https://' in url_str:
        protocol = 'https'
    else:
        protocol = 'https' if check_for_https(url_str) else 'http'
    tld_inf = tldextract.extract(url_str)
    sd, d, s = (tld_inf.subdomain, tld_inf.domain, tld_inf.suffix)
    return {
            'subdomain': sd if sd!='' else None,
            'domain': d if d!='' else None,
            'suffix': s if s!='' else None,
            'protocol': protocol
            }

def check_for_https(uri):
    """
    Short Summary
    -------------
    Determine the protocols supported by a URL

    Extended Summary
    ----------------
    Code inspired by https://github.com/creativecommons/cccatalog-api/blob/5ddee98fcb39a25d34b64894ec96ec11f61c4c31/ingestion_server/ingestion_server/cleanup.py#L152
    which is available under MIT license: https://github.com/creativecommons/cccatalog-api/blob/master/LICENSE
    """
    if 'https://' not in uri and 'http://' not in uri:
        return check_for_https('http://' + uri)
    elif 'http://' in uri:
        try:
            uri_https = uri.replace('http://', 'https://')
            result = requests.get(uri_https)
            return 200 <= result.status_code < 400
        except requests.RequestException:
            return False
    return True
    
