import requests3
from requests3 import HTTPSession

def httpbin_url(httpbin, s):
    return f"{httpbin.url}{s}"

def test_idenpotent_methods(httpbin):

    http = HTTPSession()

    for method in ('get', 'head'):

        url = httpbin_url(httpbin, f'/{method}')
        r = http.request(method, url)

        assert r.status_code == 200
