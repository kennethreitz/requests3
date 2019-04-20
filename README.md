Requests III: HTTP for Humans and Machines, alike.
==================================================

[![image](https://img.shields.io/pypi/v/requests3.svg)](https://pypi.org/project/requests/)
[![image](https://img.shields.io/pypi/l/requests3.svg)](https://pypi.org/project/requests/)
[![image](https://img.shields.io/pypi/pyversions/requests3.svg)](https://pypi.org/project/requests/)
[![image](https://img.shields.io/github/contributors/kennethreitz/requests3.svg)](https://github.com/requests/requests/graphs/contributors)
[![image](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/kennethreitz)

**If you're interested in financially supporting Requests 3 development, please [make a donation](https://cash.me/$KennethReitz). Your support helps tremendously with sustainability of motivation.**

**Requests III** is an HTTP library for Python, built for Humans and Machines, alike. **This repository is a work in progress, and the expected release timeline is "before PyCon 2020"**.

![image](https://farm5.staticflickr.com/4317/35198386374_1939af3de6_k_d.jpg)

Behold, the power of Requests III:

```pycon
>>> from requests import HTTPSession

# Make a connection pool.
>>> http = HTTPSession()

# Make a request.
>>> r = http.request('get', 'https://httpbin.org/ip')

# View response data.
>>> r.json()
{'ip': '172.69.48.124'}
```

[![image](https://raw.githubusercontent.com/requests/requests/master/docs/_static/requests-logo-small.png)](http://docs.python-requests.org/)

Requests III allows you to send *organic, grass-fed* **HTTP/1.1** & **HTTP/2** (wip) requests,
without the need for manual thought-labor. There's no need to add query
strings to your URLs, or to form-encode your POST data. Keep-alive and
HTTP connection pooling are 100% automatic, as well.

Besides, all the cool kids are doing it. Requests is one of the most
downloaded Python packages of all time, pulling in over ~1.6 million
installations *per day*!

Feature Support
---------------

Requests III is ready for today's web.

- Type-annotations for all public-facing APIs.
- Better defaults; required timeouts.
- ``async``/``await`` keyword & ``asyncio`` support.
- Compability with Python 3.6+.

While retaining all the features of `Requests Classic <https://2.python-requests.org/>`_:

-   International Domains and URLs
-   Keep-Alive & Connection Pooling
-   Sessions with Cookie Persistence
-   Browser-style SSL Verification
-   Basic/Digest Authentication
-   Elegant Key/Value Cookies
-   Automatic Decompression
-   Automatic Content Decoding
-   Unicode Response Bodies
-   Multipart File Uploads
-   HTTP(S) Proxy Support
-   Connection Timeouts
-   Streaming Downloads
-   `.netrc` Support
-   Chunked Requests

Installation
------------

To install Requests III, simply use [pipenv](http://pipenv.org/) (or pip, of
course):

``` {.sourceCode .bash}
$ pipenv install requests3
✨🍰✨
```

Satisfaction guaranteed.

Documentation
-------------

Fantastic documentation is available at
<http://3.python-requests.org/>, for a limited time only.

How to Contribute
-----------------

1.  Check for open issues or open a fresh issue to start a discussion
    around a feature idea or a bug. There is a [Contributor
    Friendly](https://github.com/requests/requests/issues?direction=desc&labels=Contributor+Friendly&page=1&sort=updated&state=open)
    tag for issues that should be ideal for people who are not very
    familiar with the codebase yet.
2.  Fork [the repository](https://github.com/requests/requests) on
    GitHub to start making your changes to the **master** branch (or
    branch off of it).
3.  Write a test which shows that the bug was fixed or that the feature
    works as expected.
4.  Send a pull request and bug the maintainer until it gets merged and
    published. :) Make sure to add yourself to
    [AUTHORS](https://github.com/requests/requests/blob/master/AUTHORS.rst).
