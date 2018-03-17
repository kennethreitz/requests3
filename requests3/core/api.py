import trio

from .http_manager import AsyncPoolManager, PoolManager
from .http_manager._backends import TrioBackend
from . import http_manager


async def request(
    method,
    url,
    timeout,
    *,
    body=None,
    headers=None,
    preload_content=False,
    pool=None,
    **kwargs
):
    """Returns a Response object, to be awaited."""
    if not pool:
        pool = AsyncPoolManager(backend=TrioBackend())
    return await pool.urlopen(
            method=method,
            url=url,
            headers=headers,
            preload_content=preload_content,
            **kwargs
        )


def blocking_request(
    method,
    url,
    timeout,
    *,
    body=None,
    headers=None,
    preload_content=False,
    pool=None,
    **kwargs
):
    """Returns a Response object."""
    if not pool:
        pool = PoolManager()
    with pool as http:
        r = http.urlopen(
            method=method,
            url=url,
            headers=headers,
            preload_content=preload_content,
            **kwargs
        )
        return r
