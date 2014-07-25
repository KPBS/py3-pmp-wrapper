"""
Module: `pmp_api.auth`

Authorization classes for signing Public Media Platform
API requests.
"""
import six
import datetime
import requests
from base64 import b64encode

from .pmp_exceptions import NoToken
from .pmp_exceptions import ExpiredToken
from .pmp_exceptions import BadRequest


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
        """Sign requests for PMP API as per PmpAuth specifications.

        Arguments:
        `request_object` -- instance of `requests.Request`

        returns:
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

    def delete_access_token(self, endpoint=None):
        """
        This method is likely unnecessary, but has been provided for
        completeness as specified in the documentation.

        Deletes access token for this account.

        returns: boolean value
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
        # Pending documentation, this may change.
        # This method works at the POST-to ('publish') server address as per
        # docs
        # However, it does not work at the standard url given by home-doc
        # For that, we must use the simpler example here:
        # curl -i "https://api-pilot.pmp.io/auth/access_token" -u \
        #     "clientid:clientsecret" -H \
        #     "Content-Type: application/x-www-form-urlencoded" -X POST

        """
        Method for retrieving an access token for use with PMP API

        See: https://github.com/publicmediaplatform/pmpdocs/ \
        wiki/Authenticating-with-the-API#grabbing-an-access-token-over-http

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

    def sign_request(self, request_obj):
        """
        Provided with a requests.Request object, this method will sign a
        request for the PMP API. It either takes a token passed in or
        it will utilize the previously requested token and set as an
        object attribute:

        Arguments:
        `request_object` -- instance of `requests.Request`

        Keyword ArgumentsL
        `token` -- Optional access token provided by PMP API

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
