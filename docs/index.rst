.. Requests documentation master file, created by
   sphinx-quickstart on Sun Feb 13 23:54:25 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Requests III: HTTP for Humans and Machines, alike.
==================================================

Release v\ |version|. (:ref:`Installation <install>`)

.. image:: https://img.shields.io/pypi/l/requests3.svg
    :target: https://pypi.org/project/requests3/

.. image:: https://img.shields.io/pypi/wheel/requests3.svg
    :target: https://pypi.org/project/requests3/

.. image:: https://img.shields.io/pypi/pyversions/requests3.svg
    :target: https://pypi.org/project/requests3/

.. image:: https://img.shields.io/badge/Say%20Thanks!-🦉-1EAEDB.svg
    :target: https://saythanks.io/to/kennethreitz

**Requests III** is an HTTP library for Python, built for Humans and Machines, alike. This repository is a work in progress, and the expected release timeline is "before PyCon 2020".

-------------------

Behold, the power of Requests III::

    >>> from requests import HTTPSession

    # Make a connection pool.
    >>> http = HTTPSession()

    # Make a request.
    >>> r = http.request('get', 'https://httpbin.org/ip')

    # View response data.
    >>> r.json()
    {'ip': '172.69.48.124'}

Requests III allows you to send *organic, grass-fed* **HTTP/1.1** & **HTTP/2** (wip) requests,
without the need for manual thought-labor. There's no need to add query
strings to your URLs, or to form-encode your POST data. Keep-alive and
HTTP connection pooling are 100% automatic, as well.

Besides, all the cool kids are doing it. Requests is one of the most
downloaded Python packages of all time, pulling in over ~1.6 million
installations *per day*!

User Testimonials
-----------------

**Microsoft**, **Google**, **Amazon**, **Salesforce**, **Heroku**, **DigitalOcean**, **RedHat**, **Twitter**, **Facebook**, **Instagram**, **Spotify**, *&c* all use **Requests** to query internal HTTPS services.

**Armin Ronacher**, creator of Flask—
    *Requests is the perfect example how beautiful an API can be with the
    right level of abstraction.*

**Matt DeBoard**—
    *I'm going to get Kenneth Reitz's Python requests module tattooed
    on my body, somehow. The whole thing.*

**Daniel Greenfeld**—
    *Nuked a 1200 LOC spaghetti code library with 10 lines of code thanks to
    Kenneth Reitz's Requests library. Today has been AWESOME.*

**Kenny Meyers**—
    *Python HTTP: When in doubt, or when not in doubt, use Requests. Beautiful,
    simple, Pythonic.*

Requests is one of the most downloaded Python packages of all time, pulling in
pulling in over ~1.6 million installations *per day*!. Join the party!

If your organization uses Requests internally, consider `supporting the development of 3.0 <https://cash.me/$KennethReitz>`_.

Feature Support
---------------

Requests III is ready for today's web.

- Support for H11 & H2 protocols.
- Type-annotations for all public-facing APIs.
- Better defaults; required timeouts.
- ``async``/``await`` keyword & ``asyncio`` support.
- Compability with Python 3.6+.

While retaining all the features of `Requests Classic <https://2.python-requests.org/>`_:

- Keep-Alive & Connection Pooling
- International Domains and URLs
- Sessions with Cookie Persistence
- Browser-style SSL Verification
- Automatic Content Decoding
- Basic/Digest Authentication
- Elegant Key/Value Cookies
- Automatic Decompression
- Unicode Response Bodies
- HTTP(S) Proxy Support
- Multipart File Uploads
- Streaming Downloads
- Connection Timeouts
- Chunked Requests
- ``.netrc`` Support


The User Guide
--------------

This part of the documentation, which is mostly prose, begins with some
background information about Requests, then focuses on step-by-step
instructions for getting the most out of Requests.

.. toctree::
   :maxdepth: 2

   user/intro
   user/install
   user/quickstart
   user/advanced
   user/authentication


The Community Guide
-------------------

This part of the documentation, which is mostly prose, details the
Requests ecosystem and community.

.. toctree::
   :maxdepth: 2

   community/sponsors
   community/recommended
   community/faq
   community/out-there
   community/support
   community/vulnerabilities
   community/updates
   community/release-process

The API Documentation / Guide
-----------------------------

If you are looking for information on a specific function, class, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api


The Contributor Guide
---------------------

If you want to contribute to the project, this part of the documentation is for
you.

.. toctree::
   :maxdepth: 3

   dev/contributing
   dev/philosophy
   dev/todo
   dev/authors

There are no more guides. You are now guideless.
Good luck.
