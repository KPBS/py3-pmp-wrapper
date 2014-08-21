# py3-pmp-wrapper ![Build Status](https://travis-ci.org/KPBS/py3-pmp-wrapper.svg?branch=master)

An application for interacting with the Public Media Platform (PMP) API. This application has been written for Python 3.3 and has been tested with Python3.3 and Python3.4. The full documentation for this application is located [here](http://api.kpbs.org/media/docs/py3-pmp-wrapper/docs/). 

To find out more about the Public Media Platform API, [consult the documentation](https://github.com/publicmediaplatform/pmpdocs/wiki).

## Installation

This package may be installed using `pip`:

```
pip install py3-pmp-wrapper
```

## Quickstart

First, create a `pmp_client.Client` object and pass it the entry-point to the application:

```python
>>> from pmp_api import Client
>>> client = Client("https://api.pmp.io")
```

#### Generate Access Token

After that, you will need to authenticate your client. To authenticate, pass in your client-id and client-secret to the `gain_access` method. You should already have a client-id and client-secret, but if not see below. 

```python
>>> client.gain_access(CLIENT-ID, CLIENT-SECRET) # This is NOT a username/password combination
```

#### Making Requests

Now, we're ready to make requests of the PMP API:

```python
>>> home_doc = client.home() # Get homedoc
>>> random_request = client.get("https://Some/arbitrary/endpoint?params=someparam")
>>> random_request
<Navigable Doc: https://Some/arbitrary/endpoint?params=someparam>
>>> client.document # Most recent result is saved here
<NavigableDoc: https://Some/arbitrary/endpoint?params=someparam>
```

The client will automatically sign all requests and it should renew your access token if it expires. 

#### Navigating
   
Using the fetched document's `navigation` object, the `Client` can follow navigation, if it's present:

```python
>>> client.next() # If the document defines a 'next' navigation element, we can follow it
<NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID&offset=10>
>>> client.prev() # Same as above, returns None if nothing there...
>>>
>>> client.last()  # requests 'last' page of results as given by document
>>> client.first() # requests 'first' page of results as given by document
```

> Keep in mind: each request here fetches a new document and sets the `client.document` attribute to the current document. 

We can also go `back` or `forward`, like a browser, re-requesting previous documents:

```python
>>> client.document
<NavigableDoc: https://api-pilot.pmp.io/docs?params=someparam>
>>> client.back()  # This issues a new request
<NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID>
>>> client.forward() 
<NavigableDoc: https://api-pilot.pmp.io/docs?params=someparam>
```

#### Using URNs

Most of the useful navigation is done via `urn`, the primary method for accessing content, and the Client object provides a `query` method for use with a `urn`. For example, let's look at `urn:collectiondoc:query:docs`, which contains information for querying documents.

```python
>>> client.query('urn:collectiondoc:query:docs', params={"tag": "samplecontent", "profile": "story"})
<NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID>
>>> client.document.items
{ ITEMS ... }
```

## NavigableDoc objects

To really get interesting information back, we need to have some way of managing it. For this reason, a `Client` object returns `NavigableDoc` elements. These have a number of methods and properties, which should make it easier to extract information from the document.

```python
>>> document = client.query('urn:collectiondoc:query:docs', params={"tag": "samplecontent", "profile": "story"})
<NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID> # returns NavigableDoc
>>> document.links
{'item': [{'href': 'https://api-pilot.pmp.io/docs/SOMEGUID ...
>>> document.items
[{'attributes': {'valid': {'to': '3014-07-29T18:08:11+00:00', 'from': ...
>>> document.querylinks
[{'rels': ['urn:collectiondoc:query:users'], 'href-template': ...
```

#### Querying 

In order to get interesting results back, we generally want to issue queries, but it can be tough to remember how to make queries. The `NavigableDoc` has a `template` method that will reveal what params are available for a query and you can use the `Client` to create a query with these params:

```python
>>> document.template('urn:collectiondoc:query:docs')
'https://api-pilot.pmp.io/docs{?guid,limit,offset,tag,collection,text,searchsort,has,author,distributor,distributorgroup,startdate,enddate,profile,language}'
>>> client.query('urn:collectiondoc:query:docs', params={'has': 'audio', 'language': 'en'})
<NavigableDoc: https://api-pilot.pmp.io/docs/SOMEQUERY>
```

The document also has a query method which will create well-formed queries for you, but it will raise a `BadQuery` exception if you pass it a set of invalid parameters, telling you which of those parameters are invalid:

```python
>>> document.query('urn:collectiondoc:query:docs',params={'has': 'audio', 'language': 'en'})
'https://api-pilot.pmp.io/docs?language=en&has=audio'
>>> document.query('urn:collectiondoc:query:docs',params={'Not-a-param': 'Error', 'profile': 'story'})
Traceback (most recent call last):
...
  raise BadQuery(errmsg.format(badstuff))
pmp_api.core.exceptions.BadQuery: Query param does not exist: {'Not-a-param'}
```


(For values accepted by query keys, consult the [PMP documentation](https://github.com/publicmediaplatform/pmpdocs/wiki)

#### Options and Query-Types

We can also find all options associated with the `urn`:

```python
>>> document.options('urn:collectiondoc:query:docs')
{'rels': ['urn:collectiondoc:query:docs'], 'href-template': ...
```

What if we want to know which `urns` are listed at a particular endpoint? We must ask the document for its `query_types`:

```python
>>> for item in document.query_types():
...     print(item)
('Query for users', ['urn:collectiondoc:query:users'])
('Query for schemas', ['urn:collectiondoc:query:schemas'])
('Access documents', ['urn:collectiondoc:hreftpl:docs'])
('Query for documents', ['urn:collectiondoc:query:docs'])
etc.
```

#### All Results

Finally, you can always retrieve *all* of the results inside a document by acessing its `collectiondoc` attribute. This will return a dictionary of *all* values contained in the document:

```python
>>> document.collectiondoc
{ALL-The_Data ...}
```

You can get or set values directly this way, or you can use the `edit` method, which requires knowing exactly where the data is located (and if you are not careful, it's easy to make a document invalid in this way by clobbering a `list` with a `string` for instance). 

To use the `edit` method, pass in a tuple or list of keys/indices to where the data is located:

```python
>>> document.edit(['attributes', 'guid'], "NEW GUID")
{'guid': "NEW GUID", etc.}
>>> document.edit(['links', 'navigation', 0, 'rels'], "NEW REL")

```

And you can get a json dump of the data inside a `NavigableDoc` (for submitting it back to PMP, for instance) by calling its serialize method:

```python
>>> document.serialize()
'{ALL-The_Data ...}'
```

## Credentials

The PMP API uses OAUTH2, which means that you need a client-id and client-secret in order to receive an access token and to use the application.

In order to request access, you must already have a username/password. Only the maintainers of PMP can issue a username/password. This application has been written and maintained by a third-party and neither this application nor the maintainers can issue username/password combinations.

### Generating Credentials

To generate new client_id/client_secret in order to access the PMP API, you can either issue a `curl` request or you can use the `pmp_api.core.access` module, which will create read-only credentials.

##### Via Curl

```
curl --user pmpuser:pmpsecret \
     -X POST "https://publish-pilot.pmp.io/auth/credentials" \
     -d "scope=read" \
     -d "token_expires_in=1380000" \
     -d "label=somethingCool" \
     -L \
     -m 5 \
```
##### Issuing Credentials Using This Application

If you do not have a client_id/client_secret for your application, you can create a PmPAccess object and have it generate credentials for you using your username and password:

```python
>>> from pmp_api.core.access import PmpAccess
>>> pmp_access = PmpAccess(username, password)
>>> pmp_access.generate_new_credentials(PMP_API_AUTHENTICATION_ENDPOINT, LABEL)
(CLIENT_ID, CLIENT_SECRET)
```
