# py3-pmp-wrapper

An application for interacting with the Public Media Platform (PMP) API. This application has been written for Python 3.3 and has been tested with Python3.3 and Python3.4. The documentation for this application is located (!here!(almost ready)). To find out more about the Public Media Platform API, [consult the documentation](https://github.com/publicmediaplatform/pmpdocs/wiki).


## How to Query the PMP API

First, create a `pmp_client.Client` object and pass it the entry-point to the application:

```python
>>> from pmp_api.pmp_client import Client
>>> client = Client("https://api-pilot.pmp.io")
```

After that, you will need to authenticate your client. To authenticate, pass in your client-id and client-secret to the `gain_access` method. You should already have a client-id and/or client-secret, but if not see below. 

```python
>>> client.gain_access(CLIENT-ID, CLIENT-SECRET) # This is NOT a username/password combination
```

Now, we're ready to make requests of the PMP API:

```python
>>> home_doc = client.home() # Get homedoc
>>> random_request = client.get("https://Some/arbitrary/endpoint?params=someparam")
>>> random_request
<Navigable Doc: https://Some/arbitrary/endpoint?params=someparam>
```

The client will automatically sign all requests and it should renew your access token if and it expires. 

Most of the useful navigation is done via `urn`, the primary method for accessing content, and the `Client` object provides a number of ways to get information in response to a `urn`. For example, let's look at `urn:collectiondoc:query:docs`, which contains information for querying documents.

```python
>>> client.query('urn:collectiondoc:query:docs', params={"tag": "samplecontent", "profile": "story"})
<NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID>
>>> client.document # Most recent result is saved here
<NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID>
>>> client.next() # If the document defines a 'next' navigation element, we can follow it
<NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID&offset=10>
>>> client.prev() # Same as above, returns None if nothing there...
>>>
```

We can also go `back` or `forward`, like a browser, re-requesting the previous document:

```python
>>> client.back() 
<NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID>
```

## What's this NavigableDoc object?

To really get interesting information back, we need to have some way of managing it. For this reason, the `Client` object returns `NavigableDoc` elements. These have a number of methods and properties, which should make it easier to extract information from the document.

```python
>>> client.query('urn:collectiondoc:query:docs', params={"tag": "samplecontent", "profile": "story"})
<NavigableDoc: https://api-pilot.pmp.io/docs?guid=SOME_GUID> # returns NavigableDoc
>>> client.document.links
{'item': [{'href': 'https://api-pilot.pmp.io/docs/SOMEGUID ...
>>> client.document.items
[{'attributes': {'valid': {'to': '3014-07-29T18:08:11+00:00', 'from': ...
>>> client.document.querylinks
[{'rels': ['urn:collectiondoc:query:users'], 'href-template': ...
```

In order to get interesting results back, we generally want to issue queries, but it can be tough to know how to make queries. The `NavigableDoc` object can help with that.

```python
>>> client.document.template('urn:collectiondoc:query:docs')
'https://api-pilot.pmp.io/docs{?guid,limit,offset,tag,collection,text,searchsort,has,author,distributor,distributorgroup,startdate,enddate,profile,language}'
```

In addition, we can find options associated with the `urn`:
```python
>>> client.document.options('urn:collectiondoc:query:docs')
{'rels': ['urn:collectiondoc:query:docs'], 'href-template': ...
```

What if we want to know which `urn`s are listed at a particular endpoint? We must ask the document for its query_types:

```python
>>> for item in client.document.query_types():
...     print(item)
('Query for users', ['urn:collectiondoc:query:users'])
('Query for schemas', ['urn:collectiondoc:query:schemas'])
('Access documents', ['urn:collectiondoc:hreftpl:docs'])
('Query for documents', ['urn:collectiondoc:query:docs'])
etc.
```

To see more examples and learn more about how to use the `Client` and `NavigableDoc` objects, consult the documentation (LINK).

## Lower Level requests of PMP API

For most things, you can use the `Client` object, but there are lower-level objects in this application, and these can be used directly should have an application that needs finer control over authenticating or requesting results from the PMP API.

### Using a PmpAuth object to get an access token

We will need a PmpAuth object to sign all of our requests of the PMP API, so create a new PmpAuth object:
```python
>>> from pmp_api.core.auth import PmpAuth
>>> pmp_auth = PmpAuth(CLIENT_ID, CLIENT_SECRET)
```

For most applications, we'll only need to do this once per session. A PmpAuth object will remember its `access_token` and it will raise an exception when that token has expired. 

### Making requests
Now that you have a PmpAuth object with a valid access token, you can create a PmpConnector that will issue signed requests:

```python
>>> from pmp_api.core.conn import PmpConnector
>>> pmp_connect = PmpConnector(pmp_auth)
>>> pmp_connect.get("https://api-pilot.pmp.io/docs")
{...DICTIONARY OF VALUES IN RESPONSE...}
```

Every link you'd like to retrieve from the PMP API can be retrieved using your connector object:
```python
>>> pmp_connect.get("https://api-pilot.pmp.io")
>>> pmp_connect.get("https://api-pilot.pmp.io/docs")
>>> pmp_connect.get("https://api-pilot.pmp.io/schemas")
>>> etc.
```

This method will automatically return the JSON returned by the endpoint. In addition, the connector will automatically renew the access_token if it expires.

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
(CLIENT_ID, CLIENT_SECRET, EXPIRATION)
```

