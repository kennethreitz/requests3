# -*- coding: utf-8 -*-
"""
requests.adapters
~~~~~~~~~~~~~~~~~

This module contains the transport adapters that Requests uses to define
and maintain connections.
"""

import os.path
import socket

import rfc3986
from . import core

from .http_models import Response, AsyncResponse
from ._basics import urlparse, basestring
from .http_utils import (
    DEFAULT_CA_BUNDLE_PATH,
    get_encoding_from_headers,
    prepend_scheme_if_needed,
    get_auth_from_url,
    urldefragauth,
    select_proxy,
)
from ._structures import HTTPHeaderDict
from .http_cookies import extract_cookies_to_jar
from .exceptions import (
    ConnectionError,
    ConnectTimeout,
    ReadTimeout,
    SSLError,
    ProxyError,
    RetryError,
    InvalidScheme,
)
from .http_auth import _basic_auth_str

try:
    from .core._http.contrib.socks import SOCKSProxyManager
except ImportError:

    def SOCKSProxyManager(*args, **kwargs):
        raise InvalidScheme("Missing dependencies for SOCKS support.")


DEFAULT_POOLBLOCK = False
DEFAULT_POOLSIZE = 10
DEFAULT_RETRIES = 0
DEFAULT_POOL_TIMEOUT = None


def _pool_kwargs(verify, cert):
    """Create a dictionary of keyword arguments to pass to a
    :class:`PoolManager <urllib3.poolmanager.PoolManager>` with the
    necessary SSL configuration.

    :param verify: Whether we should actually verify the certificate;
                   optionally a path to a CA certificate bundle or
                   directory of CA certificates.
    :param cert: The path to the client certificate and key, if any.
                 This can either be the path to the certificate and
                 key concatenated in a single file, or as a tuple of
                 (cert_file, key_file).
    """
    pool_kwargs = {}
    if verify:
        cert_loc = None
        # Allow self-specified cert location.
        if verify is not True:
            cert_loc = verify
        if not cert_loc:
            cert_loc = DEFAULT_CA_BUNDLE_PATH
        if not cert_loc or not os.path.exists(cert_loc):
            raise IOError(
                "Could not find a suitable TLS CA certificate bundle, "
                "invalid path: {0}".format(cert_loc)
            )

        pool_kwargs["cert_reqs"] = "CERT_REQUIRED"
        if not os.path.isdir(cert_loc):
            pool_kwargs["ca_certs"] = cert_loc
            pool_kwargs["ca_cert_dir"] = None
        else:
            pool_kwargs["ca_cert_dir"] = cert_loc
            pool_kwargs["ca_certs"] = None
    else:
        pool_kwargs["cert_reqs"] = "CERT_NONE"
        pool_kwargs["ca_certs"] = None
        pool_kwargs["ca_cert_dir"] = None
    if cert:
        if not isinstance(cert, basestring):
            pool_kwargs["cert_file"] = cert[0]
            pool_kwargs["key_file"] = cert[1]
        else:
            pool_kwargs["cert_file"] = cert
            pool_kwargs["key_file"] = None
        cert_file = pool_kwargs["cert_file"]
        key_file = pool_kwargs["key_file"]
        if cert_file and not os.path.exists(cert_file):
            raise IOError(
                "Could not find the TLS certificate file, "
                "invalid path: {0}".format(cert_file)
            )

        if key_file and not os.path.exists(key_file):
            raise IOError(
                "Could not find the TLS key file, "
                "invalid path: {0}".format(key_file)
            )

    return pool_kwargs


class BaseAdapter(object):
    """The Base Transport Adapter"""

    def __init__(self):
        super(BaseAdapter, self).__init__()

    def send(
        self,
        request,
        stream=False,
        timeout=None,
        verify=True,
        cert=None,
        proxies=None,
    ):
        """Sends PreparedRequest object. Returns Response object.

        :param request: The :class:`PreparedRequest <PreparedRequest>` being sent.
        :param stream: (optional) Whether to stream the request content.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use
        :param cert: (optional) Any user-provided SSL certificate to be trusted.
        :param proxies: (optional) The proxies dictionary to apply to the request.
        """
        raise NotImplementedError

    def close(self):
        """Cleans up adapter specific items."""
        raise NotImplementedError


class HTTPAdapter(BaseAdapter):
    """The built-in HTTP Adapter for urllib3.

    Provides a general-case interface for Requests sessions to contact HTTP and
    HTTPS urls by implementing the Transport Adapter interface. This class will
    usually be created by the :class:`Session <Session>` class under the
    covers.

    :param pool_connections: The number of urllib3 connection pools to cache.
    :param pool_maxsize: The maximum number of connections to save in the pool.
    :param max_retries: The maximum number of retries each connection
        should attempt. Note, this applies only to failed DNS lookups, socket
        connections and connection timeouts, never to requests where data has
        made it to the server. By default, Requests does not retry failed
        connections. If you need granular control over the conditions under
        which we retry a request, import urllib3's ``Retry`` class and pass
        that instead.
    :param pool_block: Whether the connection pool should block for connections.

    Usage::

      >>> import requests
      >>> s = requests.Session()
      >>> a = requests.adapters.HTTPAdapter(max_retries=3)
      >>> s.mount('http://', a)
    """

    __attrs__ = [
        "max_retries",
        "config",
        "_pool_connections",
        "_pool_maxsize",
        "_pool_block",
    ]

    def __init__(self):
        super(HTTPAdapter, self).__init__()
        self.client = core.http3.Client()

    def __getstate__(self):
        return {attr: getattr(self, attr, None) for attr in self.__attrs__}

    def __setstate__(self, state):
        # Can't handle by adding 'proxy_manager' to self.__attrs__ because
        # self.poolmanager uses a lambda function, which isn't pickleable.
        self.proxy_manager = {}
        self.config = {}
        for attr, value in state.items():
            setattr(self, attr, value)
        self.init_poolmanager(
            self._pool_connections, self._pool_maxsize, block=self._pool_block
        )

    def build_response(self, req, resp):
        """Builds a :class:`Response <requests.Response>` object from a urllib3
        response. This should not be called from user code, and is only exposed
        for use when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`

        :param req: The :class:`PreparedRequest <PreparedRequest>` used to generate the response.
        :param resp: The urllib3 response object.
        :rtype: requests.Response
        """
        response = Response()
        # Fallback to None if there's no status_code, for whatever reason.
        response.status_code = getattr(resp, "status_code", None)
        # Make headers case-insensitive.
        response.headers = HTTPHeaderDict(getattr(resp, "headers", {}))
        # Set encoding.
        response.encoding = get_encoding_from_headers(response.headers)
        response.protocol = getattr(resp, "protocol", None)
        response.raw = resp
        response.reason = getattr(resp, "reason_phrase", None)
        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url
        # Add new cookies from the server.
        extract_cookies_to_jar(response.cookies, req, resp)
        # Give the Response some context.
        response.request = req
        response.connection = self
        return response

    def request_url(self, request, proxies):
        """Obtain the url to use when making the final request.

        If the message is being sent through a HTTP proxy, the full URL has to
        be used. Otherwise, we should only use the path portion of the URL.

        This should not be called from user code, and is only exposed for use
        when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param request: The :class:`PreparedRequest <PreparedRequest>` being sent.
        :param proxies: A dictionary of schemes or schemes and hosts to proxy URLs.
        :rtype: str
        """
        # proxy = select_proxy(request.url, proxies)
        # scheme = urlparse(request.url).scheme
        # is_proxied_http_request = proxy and scheme != "https"
        # using_socks_proxy = False
        # if proxy:
        # proxy_scheme = urlparse(proxy).scheme.lower()
        # using_socks_proxy = proxy_scheme.startswith("socks")
        # url = request.path_url
        # if is_proxied_http_request and not using_socks_proxy:
        # url = urldefragauth(request.url)
        return request.url

    def add_headers(self, request, **kwargs):
        """Add any headers needed by the connection. As of v2.0 this does
        nothing by default, but is left for overriding by users that subclass
        the :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        This should not be called from user code, and is only exposed for use
        when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param request: The :class:`PreparedRequest <PreparedRequest>` to add headers to.
        :param kwargs: The keyword arguments from the call to send().
        """
        pass

    def proxy_headers(self, proxy):
        """Returns a dictionary of the headers to add to any request sent
        through a proxy. This works with urllib3 magic to ensure that they are
        correctly sent to the proxy, rather than in a tunnelled request if
        CONNECT is being used.

        This should not be called from user code, and is only exposed for use
        when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param proxies: The url of the proxy being used for this request.
        :rtype: dict
        """
        headers = {}
        username, password = get_auth_from_url(proxy)
        if username:
            headers["Proxy-Authorization"] = _basic_auth_str(
                username, password
            )
        return headers

    def send(
        self,
        request,
        stream=False,
        timeout=None,
        verify=True,
        cert=None,
        proxies=None,
    ):
        """Sends PreparedRequest object. Returns Response object.

        :param request: The :class:`PreparedRequest <PreparedRequest>` being sent.
        :param stream: (optional) Whether to stream the request content.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple or urllib3 Timeout object
        :param verify: (optional) Either a boolean, in which case it controls whether
            we verify the server's TLS certificate, or a string, in which case it
            must be a path to a CA bundle to use
        :param cert: (optional) Any user-provided SSL certificate to be trusted.
        :param proxies: (optional) The proxies dictionary to apply to the request.
        :rtype: requests.Response
        """
        url = self.request_url(request, proxies)
        self.add_headers(request)
        chunked = not (
            request.body is None or "Content-Length" in request.headers
        )
        if isinstance(timeout, tuple):
            try:
                connect, read = timeout
            except ValueError as e:
                # this may raise a string formatting error.
                err = (
                    "Invalid timeout {0}. Pass a (connect, read) "
                    "timeout tuple, or a single float to set "
                    "both timeouts to the same value".format(timeout)
                )
                raise ValueError(err)
        try:
            resp = core.blocking_request(
                method=request.method,
                url=url,
                data=request.body,
                headers=[(k, request.headers[k]) for k in request.headers],
                allow_redirects=False,
                # assert_same_host=False,
                # stream=False,
                # decode_content=False,
                timeout=timeout,
                # enforce_content_length=True,
                client=self.client,
            )

        except (core.http3.exceptions.ProtocolError, socket.error) as err:
            raise ConnectionError(err, request=request)

        except core.http3.exceptions.PoolTimeout as e:
            raise ConnectionError(e, request=request)

        except (core.http3.exceptions.HttpError,) as e:

            if isinstance(e, core.http3.exceptions.PoolTimeout.ReadTimeout):
                raise core.http3.exceptions.PoolTimeout.ReadTimeout(
                    e, request=request
                )

            else:
                raise

        return self.build_response(request, resp)


class AsyncHTTPAdapter(HTTPAdapter):
    """docstring for AsyncHTTPAdapter"""

    def __init__(self, backend=None, *args, **kwargs):
        super(AsyncHTTPAdapter, self).__init__(*args, **kwargs)
        self.client = core.http3.AsyncClient()

    async def build_response(self, req, resp):
        """Builds a :class:`Response <requests.Response>` object from a urllib3
        response. This should not be called from user code, and is only exposed
        for use when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`

        :param req: The :class:`PreparedRequest <PreparedRequest>` used to generate the response.
        :param resp: The urllib3 response object.
        :rtype: requests.Response
        """
        response = AsyncResponse()
        # Fallback to None if there's no status_code, for whatever reason.
        response.status_code = getattr(resp, "status_code", None)
        # Make headers case-insensitive.
        response.headers = HTTPHeaderDict(getattr(resp, "headers", {}))
        # Set encoding.
        response.encoding = get_encoding_from_headers(response.headers)
        response.raw = resp
        response.reason = getattr(resp, "reason_phrase", None)
        response.protocol = getattr(resp, "protocol", None)
        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url
        # Add new cookies from the server.
        extract_cookies_to_jar(response.cookies, req, resp)
        # Give the Response some context.
        response.request = req
        response.connection = self
        return response

    def close(self):
        """Disposes of any internal state.

        Currently, this closes the PoolManager and any active ProxyManager,
        which closes any pooled connections.
        """
        # self.poolmanager.clear()
        # for proxy in self.proxy_manager.values():
        # proxy.clear()
        pass

    async def send(
        self,
        request,
        stream=False,
        timeout=None,
        verify=True,
        cert=None,
        proxies=None,
    ):
        """Sends PreparedRequest object. Returns Response object.

        :param request: The :class:`PreparedRequest <PreparedRequest>` being sent.
        :param stream: (optional) Whether to stream the request content.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple or urllib3 Timeout object
        :param verify: (optional) Either a boolean, in which case it controls whether
            we verify the server's TLS certificate, or a string, in which case it
            must be a path to a CA bundle to use
        :param cert: (optional) Any user-provided SSL certificate to be trusted.
        :param proxies: (optional) The proxies dictionary to apply to the request.
        :rtype: requests.Response
        """
        # conn = self.get_connection(request.url, proxies, verify, cert)

        url = self.request_url(request, proxies)
        self.add_headers(request)
        chunked = not (
            request.body is None or "Content-Length" in request.headers
        )
        if isinstance(timeout, tuple):
            try:
                connect, read = timeout
                # timeout = TimeoutSauce(connect=connect, read=read)
            except ValueError as e:
                # this may raise a string formatting error.
                err = (
                    "Invalid timeout {0}. Pass a (connect, read) "
                    "timeout tuple, or a single float to set "
                    "both timeouts to the same value".format(timeout)
                )
                raise ValueError(err)
        #
        # elif isinstance(timeout, TimeoutSauce):
        # pass
        # else:
        # timeout = TimeoutSauce(connect=timeout, read=timeout)
        try:
            resp = await core.request(
                method=request.method,
                url=url,
                data=request.body,
                headers=[(k, request.headers[k]) for k in request.headers],
                allow_redirects=False,
                # redirect=False,
                # assert_same_host=False,
                # preload_content=False,
                # decode_content=False,
                # retries=self.max_retries,
                timeout=timeout,
                # enforce_content_length=True,
                client=self.client,
            )

        except (core.http3.exceptions.ProtocolError, socket.error) as err:
            raise ConnectionError(err, request=request)

        except core.http3.exceptions.PoolTimeout as e:
            raise ConnectionError(e, request=request)

        except (core.http3.exceptions.HttpError,) as e:

            if isinstance(e, core.http3.exceptions.PoolTimeout.ReadTimeout):
                raise core.http3.exceptions.PoolTimeout.ReadTimeout(
                    e, request=request
                )

            else:
                raise

        return await self.build_response(request, resp)
