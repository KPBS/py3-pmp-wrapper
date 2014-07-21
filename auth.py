"""
Module: `pmp_api.auth`

Authorization classes for signing Public Media Platform
API requests.
"""
import six
import datetime
import requests
import json
from base64 import b64encode

from .pmp_exceptions import NoToken
from .pmp_exceptions import ExpiredToken
from .pmp_exceptions import BadRequest


class PmpAccess(object):
    """Access class for Public Media Platform credentials.
    See: https://github.com/publicmediaplatform/pmpdocs/ \
    wiki/Authenticating-with-the-API

    Requires a username/password combination approved for use in the PMP Api.

    Methods include:
    generate_new_credentials -- generates new client_id/client_secret
    remove_credentials -- revokes client_id/client_secret for account

    Returns:
    `pmp_api.auth.PmpAuthorization` instance
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.client_id = None
        self.client_secret = None
        self.expiration = None

    def generate_new_credentials(self, endpoint, label,
                                 scope="read", token_expiry="200000"):
        """
        Method for creating new credentials for an account. This
        should not need to be used often (if at all). Credentials
        can also be generated with a curl post to the PMP
        Auth endpoint with the proper parameters (see auth link from docs)

        Arguments:
        `endpoint` -- url to query for credentials
        `label` -- User-set label for credentials

        Keyword Arguments:
        `scope` -- read || write permissions for PMP access. Default: "read"
        `token_expiry` -- expiration for PMP credentials. Default: "2000000"

        returns: (client_id, client_secret) :: (String, String) or raises error
        """
        payload = {'label': label,
                   'scope': scope,
                   'token_expires_in': token_expiry}

        response = requests.post(endpoint,
                                 auth=(self.username, self.password),
                                 data=payload,
                                 allow_redirects=True,
                                 timeout=5.0)
        if response.ok:
            result = json.loads(response.json())
            client_id = result.get('client_id', '')
            client_secret = result.get('client_secret', '')
            self.client = client_id
            self.client_secret = client_secret
            self.expiration = token_expiry
        else:
            raise BadRequest("No response from endpoint: {}".format(endpoint))

        return client_id, client_secret

    def remove_credentials(self, endpoint):
        """
        Revokes credentials for the PmpAuth object's username/password. This
        may be necessary if credentials are ever compromised.

        To revoke credentials, pass in endpoint
        with the client_id at the end:

        /auth/credentials/{client_id}

        returns: True || False
        """
        res = requests.delete(endpoint,
                              auth=(self.username,
                                    self.password),
                              allow_redirects=True)

        if res.status_code == 204:
            return True
        else:
            errmsg = "Improper status code returned (should be 204,"
            errmsg += " according to PMP Auth Documentation). Endpoint:{}"
            raise BadRequest(errmsg.format(endpoint))


class PmpAuth(object):
    """
    Authorization class for interacting with PMP API.

    With a working client-id and client-secret, the PmpAuth class works
    to retrieve access tokens and it uses those tokens to  authenticate
    all requests made with the PMP API.

    Must be instantiated with a working client_id/client_secret

    Methods:

    `get_access_token(endpoint)` -- retrieves new access token by posting
    to the included endpoint

    `sign_request(endpoint)` -- uses access_token to sign requests for
    the resource

    returns:
    PmPAuth object
    """

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires = None
        self.token_issued = None

    def _auth_header(self):
        """Sign requests for PMP API as per PmpAuth specifications.

        Arguments:
        `request_object` -- instance of `requests.Request`

        Returns:
        instance of `requests.Request` (signed)
        """
        unencoded_sig = "{}:{}".format(self.client_id, self.client_secret)
        unencoded_sig = bytes(unencoded_sig, encoding="UTF-8")
        if six.PY3:
            signature = b64encode(unencoded_sig).decode()
        else:
            signature = b64encode(unencoded_sig)

        headers = {'Authorization': "Basic {}".format(signature),
                   'Content-Type': 'application/x-www-form-urlencoded'}

        return headers

    def get_access_token(self, endpoint):
        """
        Method for retrieving an access token for use with PMP API

        See: https://github.com/publicmediaplatform/pmpdocs/ \
        wiki/Authenticating-with-the-API#grabbing-an-access-token-over-http
        """
        params = {'grant_type': 'client_credentials'}
        headers = self._auth_header()
        response = requests.post(endpoint,
                                 params=params,
                                 headers=headers)
        if response.ok:
            result = json.loads(response.content.decode())
            self.access_token = result.get('access_token', None)
            expiration = result.get('token_expires_in', None)
            issue_time = result.get('token_issue_date', None)

            expires = datetime.timedelta(seconds=expiration)
            time_format = "%Y-%m-%dT%H:%M:%S+00:00"
            self.token_issued = datetime.datetime.strptime(issue_time,
                                                           time_format)
            self.token_expires = self.token_issued + expires

        if self.access_token is None:
            raise NoToken("Access Token missing: {}".format(endpoint))

        return self.access_token

    def sign_request(self, request_obj, token=None,
                     content_type='collection+json'):
        """
        Provided with a requests.Request object, this method will sign a
        request for the PMP API. It either takes a token passed in or
        it will utilize the previously requested token and set as an
        object attribute:

        Arguments:
        `request_object` -- instance of `requests.Request`

        Keyword ArgumentsL
        `token` -- Optional access token provided by PMP API

        Returns:
        instance of `requests.Request` (signed)
        """
        now = datetime.datetime.utcnow()
        if token is None and self.access_token is None:
            raise NoToken("Access Token missing and needed to sign request")

        elif self.token_expires < now:
            errmsg = "Access token expired: create new access token"
            errmsg += " You may use get_access_token method of PmpAuth object."
            raise ExpiredToken(errmsg)

        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}

        content_types = {'collection+json': 'application/vnd.collection.doc+json',
                         'json': 'application/json',
                         'text': 'application/x-www-form-urlencoded'}

        headers['Content-Type'] = content_types[content_type]

        request_obj.headers = headers
        return request_obj
