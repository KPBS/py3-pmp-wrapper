"""
.. module:: pmp_api.core.auth
   :synopsis: Core authorization object for the application

:class:`PmpAuth <PmpAuth>` classes may be used to sign all requests
with PMP API and they can also generate and revoke access-tokens.
"""
import six
import datetime
import requests
from base64 import b64encode

from .exceptions import NoToken
from .exceptions import ExpiredToken
from .exceptions import BadRequest


class PmpAuth(object):
    """This is the authorization class for interacting with PMP API.

    With a working client-id and client-secret, the :class:`PmpAuth <PmpAuth>`
    retrieves access tokens and it uses those tokens to  authenticate
    all requests made with the PMP API.

    Usage::
        
      >>> from pmp_api.core.auth import PmpAuth
      >>> auth = PmpAuth(Client_ID, CLIENT_SECRET)
      >>> auth.get_access_token(AUTH_TOKEN_ENDPOINT)
      'ACCESS-TOKEN'


    :class:`PmpAuth <PmpAuth>` objects must be instantiated with a working
    client_id/client_secret

    Args:
    `client-id`
    `client-secret`

    Methods:

    `get_access_token(endpoint)` -- retrieves new access token by posting
    to the included endpoint

    `sign_request(request_object)` -- uses access_token to sign requests for
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
        self.access_token_url = None

    def _auth_header(self):
        """Returns Basic authorization headers as specified in PMP spec.
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

    def delete_access_token(self, endpoint=None):
        """This method is likely unnecessary, but has been provided for
        completeness as specified in the documentation.

        Deletes access token for this account.

        returns: True|False
        """
        if self.access_token_url is None and endpoint is None:
            errmsg = "No access_token_url provided"
            raise BadRequest(errmsg)
        elif self.access_token_url is None:
            self.access_token_url = endpoint
        else:
            endpoint = self.access_token_url

        headers = self._auth_header()
        response = requests.delete(endpoint,
                                   headers=headers)
        if response.status_code == 204:
            return True
        else:
            return False

    def get_access_token(self, endpoint=None):
        # Pending documentation, this may become deprecated.
        # This method works at the POST-to ('publish') server address as per
        # docs
        # See alternate get_access_token2 below
        """Method for retrieving an access token for use with PMP API

        See: https://github.com/publicmediaplatform/pmpdocs/wiki/Authenticating-with-the-API#grabbing-an-access-token-over-http

        returns:
        access_token
        """
        if self.access_token_url is None and endpoint is None:
            errmsg = "No access_token_url provided"
            raise BadRequest(errmsg)
        elif self.access_token_url is None:
            self.access_token_url = endpoint
        else:
            endpoint = self.access_token_url

        params = {'grant_type': 'client_credentials'}
        headers = self._auth_header()
        response = requests.post(endpoint,
                                 params=params,
                                 headers=headers)
        if response.ok:
            result = response.json()
            self.access_token = result.get('access_token', None)

            if self.access_token is None:
                raise NoToken("Access Token missing: {}".format(endpoint))

            time_format = "%Y-%m-%dT%H:%M:%S+00:00"
            issue_time = result.get('token_issue_date', None)
            self.token_issued = datetime.datetime.strptime(issue_time,
                                                           time_format)

            expiration = result.get('token_expires_in', None)
            expires = datetime.timedelta(seconds=expiration)
            self.token_expires = datetime.datetime.utcnow() + expires
            self.access_token_url = endpoint

            return self.access_token

    def get_access_token2(self, access_token_url):
        # For the access_token urn given by homedoc, this
        # method works, based on the following example:
        # curl -i "https://api-pilot.pmp.io/auth/access_token" -u \
        #     "clientid:clientsecret" -H \
        #     "Content-Type: application/x-www-form-urlencoded" -X POST
        """Alternate access_token request method provided due to shifting spec.
        Using an `access_token_url` this method requests an access token and 
        parses the response object as a result.

        See: https://github.com/publicmediaplatform/pmpdocs/wiki/Authenticating-with-the-API#grabbing-an-access-token-over-http

        Args:
           access_token_url: http string taken from PMP API Home-Doc
        """
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(access_token_url,
                                 auth=(self.client_id, self.client_secret),
                                 headers=header)
        if response.ok:
            result = response.json()
            self.access_token = result.get('access_token', None)

            if self.access_token is None:
                errmsg = "Access Token missing: {}".format(access_token_url)
                raise NoToken(errmsg)

            time_format = "%Y-%m-%dT%H:%M:%S+00:00"
            issue_time = result.get('token_issue_date', None)
            self.token_issued = datetime.datetime.strptime(issue_time,
                                                           time_format)

            expiration = result.get('token_expires_in', None)
            expires = datetime.timedelta(seconds=expiration)
            self.token_expires = datetime.datetime.utcnow() + expires
            self.access_token_url = access_token_url

            return self.access_token

    def sign_request(self, request_obj):
        """Provided with a :class:requests.Request object, this method will sign a
        request for the PMP API. Raises ExpiredToken if token has expired
        before request has been made.

        Args:
           request_object -- instance of `requests.Request`

        returns:
           instance of `requests.Request` (signed)
        """
        now = datetime.datetime.utcnow()
        if self.access_token is None:
            raise NoToken("Access Token missing and needed to sign request")

        elif self.token_expires < now:
            errmsg = "Access token expired: create new access token"
            errmsg += " You may use get_access_token method of PmpAuth object."
            raise ExpiredToken(errmsg)

        token_signed = 'Bearer {}'.format(self.access_token)
        request_obj.headers['Authorization'] = token_signed
        return request_obj
