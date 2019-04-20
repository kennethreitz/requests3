# -*- coding: utf-8 -*-
#   __
#  /__)  _  _     _   _ _/   _
# / (   (- (/ (/ (- _)  /  _)
#          /
"""
Requests HTTP Library
~~~~~~~~~~~~~~~~~~~~~

Requests is an HTTP library, written in Python, for human beings. Basic GET
usage:

   >>> import requests
   >>> r = requests.get('https://www.python.org')
   >>> r.status_code
   200
   >>> 'Python is a programming language' in r.content
   True

... or POST:

   >>> payload = dict(key1='value1', key2='value2')
   >>> r = requests.post('https://httpbin.org/post', data=payload)
   >>> print(r.text)
   {
     ...
     "form": {
       "key2": "value2",
       "key1": "value1"
     },
     ...
   }

The other HTTP methods are supported - see `requests.api`. Full documentation
is at <http://python-requests.org>.

:copyright: (c) 2017 by Kenneth Reitz.
:license: Apache 2.0, see LICENSE for more details.
"""

import urllib3
import chardet
import warnings
from .exceptions import RequestsDependencyWarning


def check_compatibility(urllib3_version: str, chardet_version: str) -> None:
    urllib3_version = urllib3_version.split(".")  # type: ignore
    assert urllib3_version != ["dev"]  # Verify urllib3 isn't installed from git.
    # Sometimes, urllib3 only reports its version as 16.1.
    if len(urllib3_version) == 2:
        urllib3_version.append("0")  # type: ignore
    # Check urllib3 for compatibility.
    major, minor, patch = urllib3_version  # noqa: F811
    major, minor, patch = int(major), int(minor), int(patch)
    # urllib3 >= 1.21.1, <= 1.24
    assert major == 1
    assert minor >= 21
    assert minor <= 24

    # Check chardet for compatibility.
    major, minor, patch = chardet_version.split(".")[:3]
    major, minor, patch = int(major), int(minor), int(patch)  # type: ignore
    # chardet >= 3.0.2, < 3.1.0
    assert major == 3  # type: ignore
    assert minor < 1  # type: ignore
    assert patch >= 2  # type: ignore


def _check_cryptography(cryptography_version: str) -> None:
    # cryptography < 1.3.4
    try:
        cryptography_version = list(
            map(int, cryptography_version.split("."))
        )  # type: ignore
    except ValueError:
        return

    if cryptography_version < [1, 3, 4]:
        warning = "Old version of cryptography ({}) may cause slowdown.".format(
            cryptography_version
        )
        warnings.warn(warning, RequestsDependencyWarning)


# Check imported dependencies for compatibility.
try:
    check_compatibility(urllib3.__version__, chardet.__version__)
except (AssertionError, ValueError):
    warnings.warn(
        "urllib3 ({}) or chardet ({}) doesn't match a supported "
        "version!".format(urllib3.__version__, chardet.__version__),
        RequestsDependencyWarning,
    )

# Attempt to enable urllib3's SNI support, if possible
try:
    from urllib3.contrib import pyopenssl

    pyopenssl.inject_into_urllib3()
    # Check cryptography version
    from cryptography import __version__ as cryptography_version

    _check_cryptography(cryptography_version)
except ImportError:
    pass
# urllib3's DependencyWarnings should be silenced.
from urllib3.exceptions import DependencyWarning

warnings.simplefilter("ignore", DependencyWarning)

from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __build__, __author__, __author_email__, __license__
from .__version__ import __copyright__, __cake__

from . import utils
from .http_models import Request, Response, PreparedRequest
from .http_sessions import Session, AsyncSession
from .http_stati import codes
from .exceptions import (
    RequestException,
    Timeout,
    URLRequired,
    TooManyRedirects,
    HTTPError,
    ConnectionError,
    FileModeWarning,
    ConnectTimeout,
    ReadTimeout,
)

# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
# FileModeWarnings go off per the default.
warnings.simplefilter("default", FileModeWarning, append=True)



# -*- coding: utf-8 -*-
"""
requests.api
~~~~~~~~~~~~

This module implements the Requests API.

:copyright: (c) 2012 by Kenneth Reitz.
:license: Apache2, see LICENSE for more details.
"""

from . import http_sessions as sessions
from . import _types as types


def request(
    method: types.Method, url: types.URL, *, session: types.Session = None, **kwargs
) -> types.Response:
    """Constructs and sends a :class:`Request <Request>`.

    :param method: method for the new :class:`Request` object.
    :param url: URL for the new :class:`Request` object.
    :param session: :class:`Session` object to use for this request. If none is given, one will be provided.
    :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
    :param data: (optional) Dictionary or list of tuples ``[(key, value)]`` (will be form-encoded), bytes, or file-like object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
        to add for the file.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :type timeout: float or tuple
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :type allow_redirects: bool
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response

    Usage::

      >>> import requests
      >>> req = requests.request('GET', 'https://httpbin.org/get')
      <Response [200]>
    """
    # By using the 'with' statement we are sure the session is closed, thus we
    # avoid leaving sockets open which can trigger a ResourceWarning in some
    # cases, and look like a memory leak in others.
    session = sessions.Session() if session is None else session
    with session:
        return session.request(method=method, url=url, **kwargs)


def get(url: types.URL, *, params: types.Params = None, **kwargs) -> types.Response:
    r"""Sends a GET request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs.setdefault("allow_redirects", True)
    return request("get", url, params=params, **kwargs)

def head(url: types.URL, **kwargs) -> types.Response:
    r"""Sends a HEAD request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs.setdefault("allow_redirects", False)
    return request("head", url, **kwargs)
