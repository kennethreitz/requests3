import http3

__all__ = ["request", "blocking_request"]


async def request(
    method,
    url,
    timeout,
    *,
    data=None,
    headers=None,
    stream=False,
    client=None,
    **kwargs
):
    """Returns a Response object, to be awaited."""
    if not client:
        client = http3.AsyncClient()
    return await client.request(
        method=method,
        url=url,
        headers=headers,
        stream=stream,
        data=data,
        **kwargs
    )


def blocking_request(
    method,
    url,
    timeout,
    *,
    data=None,
    headers=None,
    stream=False,
    client=None,
    **kwargs
):
    """Returns a Response object."""
    if not client:
        client = http3.Client()
    with client as http:
        r = http.request(
            method=method,
            url=url,
            headers=headers,
            stream=stream,
            data=data,
            **kwargs
        )
        return r
