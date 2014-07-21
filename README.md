An application for making signed requests of the PMP API (Public Media Platform). This application has been written for Python 3.3 and has not been tested with other Python versions (but it should work on Python3.3 and above).


## Setup and Configuration

### Storing Credentials

Rename `config_TEMPLATE` in config directory to `config`.
Enter login, password to config file. 

If you have a client_id/client_secret for your application, enter those into the config parameters. Otherwise, generate new client_id/client_secret using the PMP API. You can do this by issuing a curl request:

```
curl --user pmpuser:pmpsecret \
     -X POST "https://publish-sandbox.pmp.io/auth/credentials" \
     -d "scope=read" \
     -d "token_expires_in=1380000" \
     -d "label=somethingCool" \
     -L \
     -m 5 \
```

Alternately, you can issue credentials for your application using the py3-pmp-wrapper.

### Issuing Credentials for Your Application

If you do not have a client_id/client_secret for your application,  you can create a PmPAccess object and have it generate credentials for you:

```Python
>>> from .auth import PmpAccess
>>> pmp_access = PmpAccess(username, password)
>>> pmp_access.generate_new_credentials(PMP_API_ENDPOINT_URL.io, LABEL)
(CLIENT_ID, CLIENT_SECRET, EXPIRATION)
```


## How to make requests of PMP API

### Using a PmpAuth object to create an access token

We will need a PmpAuth object to sign all of our requests of the PMP API. Thus, if you do not already have one, create a new PmpAuth object:
```Python
>>> from .auth import PmpAuth
>>> pmp_auth = PmpAuth(CLIENT_ID, CLIENT_SECRET)
```

With a working PmpAuth object, we will need to generate an access token in order to communicate with PMP. To do that, we use the following method:
```
>>> pmp_auth.get_access_token()
```

For most applications, we'll only need to do this once per session. A PmpAuth object will remember its `access_token` and it will let you know when that token has expired. 

### Making requests
Now that you have a PmpAuth object with a valid access token, we can use our PmpAuth object to create a PmpConnector that will make requests for us:

```Python
>>> from .conn import PmpConnector
>>> pmp_connect = PmpConnector(pmp_auth)
>>> pmp_connect.get("https://api-pilot.pmp.io/docs")
{...DICTIONARY OF VALUES IN RESPONSE...}
```

Every link you'd like to retrieve from the PMP API can be retrieved using your connector object:
```Python
>>> pmp_connect.get("https://api-pilot.pmp.io")
>>> pmp_connect.get("https://api-pilot.pmp.io/docs")
>>> pmp_connect.get("https://api-pilot.pmp.io/schemas")
>>> etc.
```


The returned value is a dictionary created from the JSON returned by the endpoint.
