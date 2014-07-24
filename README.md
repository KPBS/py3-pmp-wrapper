# py3-pmp-wrapper

An application for making signed requests of the PMP API (Public Media Platform). This application has been written for Python 3.3 and has not been tested with other Python versions (but it should work on Python3.3 and above). To find out more about the Public Media Platform API, [consult the documentation](https://github.com/publicmediaplatform/pmpdocs/wiki).

## Setup and Configuration

### Issuing Credentials

To generate new client_id/client_secret in order to access the PMP API, you can either issue a `curl` request or you can use the `pmp_api.auth` module.

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
>>> from pmp_api.auth import PmpAccess
>>> pmp_access = PmpAccess(username, password)
>>> pmp_access.generate_new_credentials(PMP_API_ENDPOINT_URL.io, LABEL)
(CLIENT_ID, CLIENT_SECRET, EXPIRATION)
```

## How to make requests of PMP API

### Using a PmpAuth object to create an access token

We will need a PmpAuth object to sign all of our requests of the PMP API, so create a new PmpAuth object:
```python
>>> from pmp_api.auth import PmpAuth
>>> pmp_auth = PmpAuth(CLIENT_ID, CLIENT_SECRET)
```

We will need to generate an access token in order to communicate with PMP. To do that, you can use the following method:
```python
>>> pmp_auth.get_access_token(ACCESS_TOKEN_URL)
```

For most applications, we'll only need to do this once per session. A PmpAuth object will remember its `access_token` and it will let you know when that token has expired. 

### Making requests
Now that you have a PmpAuth object with a valid access token, you can create a PmpConnector that will issue signed requests:

```python
>>> from pmp_api.conn import PmpConnector
>>> pmp_connect = PmpConnector(auth_object=pmp_auth)
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


## Helper Methods

A number of helper methods have been provided in the `utils` directory. These are present in order to make it easy to parse and filter the various JSON objects returned. Examples follow

#### Filter nested dictionaries for a particular key-value pair

For filtering a nested dictionary, use `json_utils.filter_dict`. This function returns a generator of dictionaries that contain the key where the associated value matches the value passed in:

```python
>>> from pmp_api.utils.json_utils import filter_dict
>>> results = pmp_connect.get("https://api-pilot.pmp.io/")
>>> list(filter_dict(results, 'rels', 'urn:collectiondoc:form:issuetoken'))
[{'href': 'https://api-pilot.pmp.io/auth/access_token', 'title': 'Issue OAuth2 Token', 'rels': ['urn:collectiondoc:form:issuetoken'], 'hints': {'docs': 'http://docs.pmp.io/wiki/Authentication-Model#token-management', 'allow': ['POST']}}]
```

#### Find all dict objects (nested or not) containing a key

For searching for a key, use `json_utils.qfind`. This function returns a generator of dictionaries that contain the key passed in:

```python
>>> from pmp_api.utils.json_utils import qfind
>>> docs = pmp_connect.get("https://api-pilot.pmp.io/docs")
>>> for item in qfind(docs, 'creator'):
...    print(item)
[{'creator': [{'href': 'https://api-pilot.pmp.io/docs/SOME-HUGE-GUID ...
```


#### Retrieve a particular dictionary with a key/value pair

If you are expecting that your filtering is only going to result in one value, you can immediately return that result and skip getting a generator object back. For this case, use `json_utils.get_dict`. 

```python
>>> from pmp_api.utils.json_utils import get_dict
>>> results = pmp_connect.get("https://api-pilot.pmp.io/")
>>> get_dict(results, 'rels', 'urn:collectiondoc:form:issuetoken')
[{'creator': [{'href': 'https://api-pilot.pmp.io/docs/SOME-HUGE-GUID
{'href': 'https://api-pilot.pmp.io/auth/access_token', 'title': 'Issue OAuth2 Token', 'rels': ['urn:collectiondoc:form:issuetoken'], 'hints': {'docs': 'http://docs.pmp.io/wiki/Authentication-Model#token-management', 'allow': ['POST']}
```

This function returns the first dictionary that matches the key/value pair and raises `NoResult` on empty search.

```python
>>> get_dict(results, 'rels', "SOME MISSING VALUE")
Traceback (most recent call last)
	  ...
NoResult: Result empty for provided arguments...
```
