An application for making signed requests of the PMP API (Public Media Platform). This application has been written for Python 3.3 only.

How to use


## Setup and Configuration

### Storing Credentials

Rename `config_TEMPLATE` in config directory to `config`.
Enter login, password to config file. 

If you have a client_id/client_secret for your application, enter those into the config parameters. Otherwise, generate new client_id/client_secret using the PMP API. You can do this either by issuing a curl request:

```
curl --user pmpuser:pmpsecret \
     -X POST "https://publish-sandbox.pmp.io/auth/credentials" \
     -d "scope=read" \
     -d "token_expires_in=1380000" \
     -d "label=somethingCool" \
     -L \
     -m 5 \
```

### Issuing Credentials for Your Application

If you do not have a client_id/client_secret for your application,  you can create a PmPAccess object and have it generate credentials for you:

```python
>>> from pmp_api.auth import PmpAccess
>>> pmp_access = PmpAccess(username, password)
>>> pmp_access.generate_new_credentials(PMP_API_ENDPOINT_URL.io, LABEL)
(CLIENT_ID, CLIENT_SECRET, EXPIRATION)
```


## How to make requests of PMP API

### Using a PmpAuth object to create an access token

We will need a PmpAuth object to sign all of our requests of the PMP API. Thus, if you do not already have one, create a new PmpAuth object:
```python
>>> pmp_auth = PmpAuth(CLIENT_ID, CLIENT_SECRET)
>>> pmp_auth.get_access_token()
```

### Making requests
Now that you have a PmpAuth object with a valid access token, you can create a connector that will make requests for you:

```python
>>> pmp_connect = PmpConnector(pmp_auth)
>>> pmp.get("https://api-pilot.pmp.io/docs")
{...DICTIONARY OF VALUES IN RESPONSE...}
```

The returned value is a dictionary created from the JSON returned by the endpoint.
