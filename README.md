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

## Storing Credentials

A config template has been provided inside the `config` directory. In addition, a convenience method for accessing these configs has also been provided. 

To use the convenience config file and config-parser, perform the following steps:

1. Rename `config/config_TEMPLATE` to 'config/config`.
2. Add your username/password to the renamed file.
3. Add your client_id/client_secret for this and other applications to the config file. 

Once these credentials are saved inside the config file, you can use the convenience method to retrieve them from the config file in the following way:

```python
>>> from pmp_api import get_configs
>>> configs = get_configs()
>>> configs['credentials']['client_id']
YOUR-CLIENT-ID
```

For questions on this creating or editing the config file, consult the documentation for [Python's ConfigParser](https://docs.python.org/3/library/configparser.html).

## How to make requests of PMP API

### Using a PmpAuth object to create an access token

We will need a PmpAuth object to sign all of our requests of the PMP API. Thus, if you do not already have one, create a new PmpAuth object:
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
