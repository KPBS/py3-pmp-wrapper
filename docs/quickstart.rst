.. _quickstart:

Quickstart
==========

To install py3-pmp-wrapper with `pip <https://pip.pypa.io>`_, just run
this in your terminal::

    $ pip install py3-pmp-wrapper

or, with `easy_install <http://pypi.python.org/pypi/setuptools>`_::

    $ easy_install py3-pmp-wrapper


Create a PMP Client
-------------------

After the application has been installed, you can create a `Client` object:

    >>> from pmp_api.pmp_client import Client
    >>> client = Client("https://api-pilot.pmp.io")


Authenticate Your Client
------------------------

With a working client, you will need to authenticate using your client-id and client-secret

    >>> client.gain_access(CLIENT-ID, CLIENT-SECRET)


Make Requests
-------------

Now you're ready to make requests:

    >>> home_doc = client.home() # Get homedoc
    >>> random_request = client.get("https://Some/arbitrary/endpoint?params=someparam")
    >>> random_request
    <Navigable Doc: https://Some/arbitrary/endpoint?params=someparam>
     >>> client.document # Most recent result is saved here
    <NavigableDoc: https://api-pilot.pmp.io/docs?params=someparam>

The `Client` will automatically sign all requests and it should renew your access token if it expires.

Navigating
----------
   
Using the fetched document's `navigation` object, the `Client` follow navigation, if it's present:

    >>> client.next() # If the document defines a 'next' navigation element, we can follow it
    <NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID&offset=10>
    >>> client.prev() # Same as above, returns None if nothing there...
    >>>
    >>> client.last()  # requests 'last' page of results as given by document
    >>> client.first() # requests 'first' page of results as given by document


We can also go `back` or `forward`, like a browser, re-requesting the previous document:


     >>> client.document
     <NavigableDoc: https://api-pilot.pmp.io/docs?params=someparam>
     >>> client.back() 
     <NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID>
     >>> client.forward()
     <NavigableDoc: https://api-pilot.pmp.io/docs?params=someparam>

.. note:: Keep in mind: each request here fetches a new document and sets the `client.document` attribute to the new **current** document. This means that future calls to `query` will use the **current** document.


Most of the useful navigation is done via `urn`, the primary method for accessing content, and the Client object provides a `query` method for use with a `urn`. For example, let's look at `urn:collectiondoc:query:docs`, which contains information for querying documents.

    >>> document = client.query('urn:collectiondoc:query:docs', params={"tag": "samplecontent", "profile": "story"})
    <NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID>

NavigableDoc objects
====================

To really get interesting information back, we need to have some way of managing it. For this reason, the `Client` object returns `NavigableDoc` elements. These have a number of methods and properties, which should make it easier to extract information from the document.

    >>> document = client.query('urn:collectiondoc:query:docs', params={"tag": "samplecontent", "profile": "story"})
    <NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID> # returns NavigableDoc
    >>> document.links
    {'item': [{'href': 'https://api-pilot.pmp.io/docs/SOMEGUID ...
    >>> client.document.items
    [{'attributes': {'valid': {'to': '3014-07-29T18:08:11+00:00', 'from': ...
    >>> document.querylinks
    [{'rels': ['urn:collectiondoc:query:users'], 'href-template': ...

In order to get interesting results back, we generally want to issue queries, but it can be tough to know how to make queries. The `NavigableDoc` object can help with that.

    >>> document.template('urn:collectiondoc:query:docs')
    'https://api-pilot.pmp.io/docs{?guid,limit,offset,tag,collection,text,searchsort,has,author,distributor,distributorgroup,startdate,enddate,profile,language}'

In addition, we can find options associated with the `urn`:

    >>> document.options('urn:collectiondoc:query:docs')
    {'rels': ['urn:collectiondoc:query:docs'], 'href-template': ...

What if we want to know which `urns` are listed at a particular endpoint? We must ask the document for its `query_types`:

    >>> for item in document.query_types():
    ...     print(item)
    ('Query for users', ['urn:collectiondoc:query:users'])
    ('Query for schemas', ['urn:collectiondoc:query:schemas'])
    ('Access documents', ['urn:collectiondoc:hreftpl:docs'])
    ('Query for documents', ['urn:collectiondoc:query:docs'])
    etc.

Finally, you can always retrieve all of the results inside a document by acessing its `collectiondoc` attribute. This will return a dictionary of all values contained in the document:

    >>> document.collectiondoc
    {ALL-The_Data ...}

This should cover most use-cases for browsing PMP API content. 
