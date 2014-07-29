"""

.. module:: pmp_api.core.access
   :synopsis: For managing application credentials

The :class:`PmpAccess <PmpAccess>` object can generate and revoke credentials
(client-id, client-secret) for use with PMP API.
"""
import requests

from .exceptions import BadRequest


class PmpAccess(object):
    """Access class for Public Media Platform credentials.
    See: https://github.com/publicmediaplatform/pmpdocs/wiki/Authenticating-with-the-API

    Requires a username/password combination approved for use in the PMP Api.

    Methods include:
    generate_new_credentials -- generates new client_id/client_secret
    remove_credentials -- revokes client_id/client_secret for account

    returns:
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

        Args:
        `endpoint` -- url to query for credentials
        `label` -- User-set label for credentials

        Kwargs:
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
            result = response.json()
            client_id = result.get('client_id', None)
            client_secret = result.get('client_secret', None)
            self.client_id = client_id
            self.client_secret = client_secret
            self.expiration = token_expiry
            return self.client_id, self.client_secret
        else:
            raise BadRequest("No response from endpoint: {}".format(endpoint))

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
