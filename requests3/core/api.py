import trio

from ._http import AsyncPoolManager, PoolManager
from ._http._backends import TrioBackend

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
            body=body,
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
            body=body,
            **kwargs
        )
        return r
