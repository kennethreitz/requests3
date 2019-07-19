import pytest


@pytest.fixture
def httpbin(httpbin):
    def gen(*url):
        url = '/'.join(url)
        return f"{httpbin.url}/{url}"

    return gen
